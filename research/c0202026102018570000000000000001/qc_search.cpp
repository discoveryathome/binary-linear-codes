#define main search_entry_point
#include "search.cpp"
#undef main
// New family: [I | circ(a) | circ(b) | circ(c)], block size 11.
// a,b odd parity and c even parity: rows have odd weight. This avoids the
// divisibility obstruction of the published [45,14,16] parent.
U rotate11(U p,int j) {return ((p<<j)|(p>>(11-j)))&2047;}
vector<U> qc_rows(const vector<U>&p){
    vector<U> r(11);
    for(int j=0;j<11;++j)for(int b=0;b<4;++b)r[j]|=rotate11(p[b],j)<<(11*b);
    return r;
}
vector<pair<int,int>> orbits(){
    vector<pair<int,int>> out;
    for(int m=1;m<2048;++m){
        int smallest=m,size=0;
        for(int j=0;j<11;++j){int x=rotate11(m,j);smallest=min(smallest,x);if(x==m)++size;}
        if(smallest==m)out.push_back({m,11/size});
    }
    return out;
}
vector<int> qc_hist(const vector<U>&p,const vector<pair<int,int>>&orb){
    auto r=qc_rows(p);vector<int> h(45);
    for(auto [m,size]:orb){
        U word=0;for(int q=m;q;q&=q-1)word^=r[__builtin_ctz((unsigned)q)];
        h[pop(word)]+=size;
    }
    return h;
}
int main(int argc,char**argv){
    if(argc!=6){cerr<<"qc_search SEED SECONDS ITERATIONS OUTPUT METHOD\n";return 2;}
    U seed=stoull(argv[1]),limit=stoull(argv[3]);double wall=stod(argv[2]);
    string method=argv[5];mt19937_64 rng(seed);auto orb=orbits();
    if(orb.size()!=187)return 3;
    auto random_polys=[&](){
        vector<U> p={1,rng()%2048,rng()%2048,rng()%2048};
        for(int j=1;j<4;++j)if(parity(p[j])!=(j<3))p[j]^=1;
        return p;
    };
    auto p=random_polys(),best=p;auto h=qc_hist(p,orb),bh=h;
    // Positive control: orbit evaluation must exactly equal all 2047 words.
    for(int test=0;test<100;++test){auto q=random_polys();if(qc_hist(q,orb)!=hist(weights(qc_rows(q)),44))return 4;}
    auto t0=chrono::steady_clock::now();clock_t c0=clock();U step=0,accepted=0,restarts=0;
    auto secs=[&](){return chrono::duration<double>(chrono::steady_clock::now()-t0).count();};
    ofstream out(argv[4]);out<<setprecision(12);
    auto emit=[&](string type){
        out<<"{\"type\":\""<<type<<"\",\"step\":"<<step<<",\"seconds\":"<<secs()
           <<",\"cpu_seconds\":"<<double(clock()-c0)/CLOCKS_PER_SEC
           <<",\"d\":"<<dist(bh)<<",\"minimum_words\":"<<bh[dist(bh)]
           <<",\"accepted\":"<<accepted<<",\"restarts\":"<<restarts
           <<",\"polynomials\":";print_rows(out,best);out<<",\"rows\":";print_rows(out,qc_rows(best));out<<"}\n";out.flush();
    };
    emit("initial");U stagnation=0;
    for(;step<limit&&(wall<=0||secs()<wall);++step){
        auto q=p;
        if(method=="random")q=random_polys();
        else {
            int j=1+rng()%3,a=rng()%11,b=rng()%10;if(b>=a)++b;
            q[j]^=(U(1)<<a)|(U(1)<<b);
            if(step%7==0){j=1+rng()%3;a=rng()%11;b=rng()%10;if(b>=a)++b;q[j]^=(U(1)<<a)|(U(1)<<b);}
        }
        auto hh=qc_hist(q,orb);
        bool accept=method=="random"||!better(h,hh);
        if(method=="anneal"&&!accept){
            // Bounded soft penalty, permitting temporary distance regression.
            double e=0,ee=0;
            for(int z=1;z<45;++z){double f=exp(-0.8*(z-17));e+=h[z]*f;ee+=hh[z]*f;}
            double temperature=0.25+2.0*(1.0-double(step%10000)/10000);
            accept=double(rng())/double(UINT64_MAX)<exp((e-ee)/temperature);
        }
        if(accept){p=q;h=hh;++accepted;}
        ++stagnation;
        if(better(hh,bh)){int d=dist(bh);best=q;bh=hh;stagnation=0;if(dist(bh)>d)emit("distance");}
        if(method!="random"&&stagnation>=20000){p=random_polys();h=qc_hist(p,orb);stagnation=0;++restarts;}
        if(step%100000==99999)emit("checkpoint");
    }
    emit("final");cerr<<"QC "<<method<<" seed "<<seed<<" steps "<<step<<" d "<<dist(bh)<<" A_d "<<bh[dist(bh)]<<"\n";
    return 0;
}
