#define main search_entry_point
#include "search.cpp"
#undef main
// For odd d, the even-weight kernel is a dimension-(k-1) subcode.
// Change its other coset by v: G'_i=G_i + parity(G_i)*v.
// Only the odd coset needs reevaluation; the even kernel is fixed.
int main(int argc,char**argv){
    if(argc!=7){cerr<<"coset_search INPUT SEED SECONDS ITERATIONS OUTPUT METHOD\n";return 2;}
    ifstream in(argv[1]);int n,k;in>>n>>k;vector<U> rows(k);for(auto&x:rows)in>>x;
    if(n>63||k>16)return 2;
    U seed=stoull(argv[2]),limit=stoull(argv[4]);double wall=stod(argv[3]);string method=argv[6];
    mt19937_64 rng(seed);vector<U> odd;vector<U> all(1<<k);int fixed=n+1;U selector=0;
    for(int i=0;i<k;++i)selector|=U(parity(rows[i]))<<i;
    if(!selector)return 3;
    for(int m=1;m<(1<<k);++m){
        int b=__builtin_ctz((unsigned)m);all[m]=all[m^(1<<b)]^rows[b];
        if(parity(m&selector))odd.push_back(all[m]);else fixed=min(fixed,pop(all[m]));
    }
    auto evaluate=[&](U v){vector<int> h(n+1);for(U x:odd)++h[pop(x^v)];return h;};
    U v=0,bv=0;auto h=evaluate(v),bh=h;int goal=dist(bh)+1;
    auto t0=chrono::steady_clock::now();clock_t c0=clock();U step=0,accepted=0,shakes=0;
    auto secs=[&](){return chrono::duration<double>(chrono::steady_clock::now()-t0).count();};
    ofstream out(argv[5]);out<<setprecision(12);
    auto emit=[&](string type){
        auto r=rows;for(int i=0;i<k;++i)if((selector>>i)&1)r[i]^=bv;
        out<<"{\"type\":\""<<type<<"\",\"step\":"<<step<<",\"seconds\":"<<secs()
           <<",\"cpu_seconds\":"<<double(clock()-c0)/CLOCKS_PER_SEC
           <<",\"d\":"<<min(fixed,dist(bh))<<",\"coset_distance\":"<<dist(bh)
           <<",\"fixed_subcode_distance\":"<<fixed<<",\"coset_minimum_words\":"<<bh[dist(bh)]
           <<",\"accepted\":"<<accepted<<",\"shakes\":"<<shakes<<",\"shift\":"<<bv
           <<",\"selector\":"<<selector<<",\"rows\":";print_rows(out,r);out<<"}\n";out.flush();
    };
    emit("initial");U stagnation=0;
    for(;step<limit&&(wall<=0||secs()<wall);++step){
        U vv=v^(U(1)<<(rng()%n));
        if(step%5==0)vv^=U(1)<<(rng()%n);
        auto hh=evaluate(vv);bool accept=!better(h,hh);
        if(method=="anneal"&&!accept){
            double e=0,ee=0;
            for(int z=0;z<=n;++z){double f=exp(-0.7*(z-goal));e+=h[z]*f;ee+=hh[z]*f;}
            double temperature=0.05+3.0*(1.0-double(step%20000)/20000);
            accept=double(rng())/double(UINT64_MAX)<exp((e-ee)/temperature);
        }
        if(accept){v=vv;h=hh;++accepted;}
        ++stagnation;
        if(!hh[0]&&better(hh,bh)){int old=dist(bh);bv=vv;bh=hh;stagnation=0;if(dist(bh)>old)emit("distance");}
        if(stagnation>=50000){
            v=bv;for(int z=0;z<3+int(rng()%5);++z)v^=U(1)<<(rng()%n);
            h=evaluate(v);stagnation=0;++shakes;
        }
        if(step%100000==99999)emit("checkpoint");
    }
    emit("final");cerr<<"coset "<<n<<","<<k<<" "<<method<<" seed="<<seed<<" steps="<<step<<" d="<<min(fixed,dist(bh))<<"\n";
    return 0;
}
