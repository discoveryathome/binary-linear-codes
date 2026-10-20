// C++17, one CPU thread, no external libraries. Search is heuristic; Python
// certificates and two exhaustive checkers are the acceptance authority.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>
#include <ctime>
using U = uint64_t;
using namespace std;
int parity(U x) { return __builtin_parityll(x); }
int pop(U x) { return __builtin_popcountll(x); }
vector<int> weights(const vector<U>& r) {
    vector<U> words(1 << r.size());
    vector<int> w(words.size());
    for (int m=1;m<(int)words.size();++m) {
        int b=__builtin_ctz((unsigned)m);
        words[m]=words[m^(1<<b)]^r[b]; w[m]=pop(words[m]);
    }
    return w;
}
vector<int> hist(const vector<int>& w,int n) {
    vector<int> h(n+1);
    for(int m=1;m<(int)w.size();++m) ++h[w[m]];
    return h;
}
int dist(const vector<int>& h) {
    for(int i=0;i<(int)h.size();++i) if(h[i]) return i;
    return 0;
}
bool better(const vector<int>& a,const vector<int>& b) {
    return lexicographical_compare(a.begin(),a.end(),b.begin(),b.end());
}
void fwht(vector<double>& a) {
    for(int half=1;half<(int)a.size();half*=2)
        for(int off=0;off<(int)a.size();off+=2*half)
            for(int j=off;j<off+half;++j) {
                double x=a[j],y=a[j+half]; a[j]=x+y;a[j+half]=x-y;
            }
}
U column(const vector<U>& r,int j) {
    U c=0;for(int i=0;i<(int)r.size();++i)c|=((r[i]>>j)&1)<<i;return c;
}
void replace(vector<U>& r,int j,U c) {
    for(int i=0;i<(int)r.size();++i)
        r[i]=(r[i]&~(U(1)<<j))|(((c>>i)&1)<<j);
}
void print_rows(ostream& o,const vector<U>& r) {
    o<<"[";for(int i=0;i<(int)r.size();++i)o<<(i?",":"")<<r[i];o<<"]";
}
int main(int argc,char**argv) {
    if(argc!=9){cerr<<"search INPUT MODE SEED WALL_SECONDS ITERATIONS OUTPUT START GOAL\n";return 2;}
    ifstream in(argv[1]);int n,k;in>>n>>k;
    if(!in||n>63||k>16||k<1)return 2;
    vector<U> r(k);for(auto&x:r)in>>x;
    string mode=argv[2],start=argv[7];U seed=stoull(argv[3]);
    double wall=stod(argv[4]);U limit=stoull(argv[5]);int goal=stoi(argv[8]);
    mt19937_64 rng(seed);int M=1<<k;
    if(start=="cold") for(int i=0;i<k;++i)r[i]=(U(1)<<i)|((rng()&((U(1)<<(n-k))-1))<<k);
    auto w=weights(r),h=hist(w,n);auto best=r;auto bh=h;
    ofstream out(argv[6]);out<<setprecision(12);
    auto t0=chrono::steady_clock::now();clock_t c0=clock();
    auto seconds=[&](){return chrono::duration<double>(chrono::steady_clock::now()-t0).count();};
    U step=0,alternatives=0,accepted=0,shakes=0;
    auto emit=[&](const string& type){
        out<<"{\"type\":\""<<type<<"\",\"step\":"<<step<<",\"seconds\":"<<seconds()
           <<",\"cpu_seconds\":"<<double(clock()-c0)/CLOCKS_PER_SEC
           <<",\"alternatives\":"<<alternatives<<",\"accepted\":"<<accepted
           <<",\"shakes\":"<<shakes<<",\"d\":"<<dist(bh)<<",\"minimum_words\":"<<bh[dist(bh)]
           <<",\"rows\":";print_rows(out,best);out<<"}\n";out.flush();
    };
    emit("initial");U last_progress=0;
    for(;step<limit && (wall<=0||seconds()<wall);++step) {
        if(mode=="blind") {
            auto rr=r;
            if(step%3==0)replace(rr,rng()%n,rng()%M);
            else for(int z=0;z<1+int(step%7==0);++z)rr[rng()%k]^=U(1)<<(rng()%n);
            auto ww=weights(rr),hh=hist(ww,n);++alternatives;
            if(!hh[0]&&!better(h,hh)){r=rr;w=ww;h=hh;++accepted;}
        } else if(mode=="walsh") {
            // Exact best replacement column for an exponential surrogate, in
            // O(k*2^k), rather than O(4^k) word/column parity evaluations.
            double beta[]={0.35,0.55,0.8,1.2};
            double b=beta[(step/(4*n))%4];int j=rng()%n;U old=column(r,j);
            vector<double> a(M);a[0]=0;
            for(int m=1;m<M;++m)a[m]=exp(-b*(w[m]-parity(m&old)-goal));
            fwht(a);U chosen=0;
            for(int c=1;c<M;++c)if(a[c]<a[chosen]-1e-10)chosen=c;
            alternatives+=M;
            if(chosen!=old) {
                replace(r,j,chosen);
                for(int m=1;m<M;++m)w[m]+=parity(m&chosen)-parity(m&old);
                h=hist(w,n);++accepted;
            }
            // Escape strict coordinate minima; search remains deterministic
            // given the seed and iteration count, independent of elapsed time.
            if(step>0 && step%(8*n)==0) {
                if(rng()%2==0){r=best;w=weights(r);h=hist(w,n);}
                for(int z=0;z<3+int(rng()%4);++z)replace(r,rng()%n,rng()%M);
                w=weights(r);h=hist(w,n);++shakes;
            }
        } else {cerr<<"unknown mode";return 2;}
        if(!h[0]&&better(h,bh)){
            int oldd=dist(bh);best=r;bh=h;last_progress=step;
            if(dist(bh)>oldd)emit("distance");
        }
        if(step%10000==9999)emit("checkpoint");
    }
    emit("final");
    cerr<<mode<<" "<<start<<" "<<n<<","<<k<<" steps="<<step
        <<" best="<<dist(bh)<<" minwords="<<bh[dist(bh)]
        <<" last_progress="<<last_progress<<" wall="<<seconds()<<"\n";
}
