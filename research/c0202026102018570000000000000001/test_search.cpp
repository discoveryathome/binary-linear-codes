#define main search_entry_point
#include "search.cpp"
#undef main
#include <cassert>
int main() {
    mt19937_64 rng(7701);
    for(int trial=0;trial<100;++trial) {
        int n=9,k=4,M=1<<k;vector<U> r(k);
        for(auto&x:r)x=rng()%512;
        auto w=weights(r);int j=rng()%n;U old=column(r,j);double beta=0.55;
        vector<double> a(M);double total=0;
        for(int m=1;m<M;++m){a[m]=exp(-beta*(w[m]-parity(m&old)));total+=a[m];}
        fwht(a);
        for(int c=0;c<M;++c) {
            auto rr=r;replace(rr,j,c);auto ww=weights(rr);
            double exact=0;for(int m=1;m<M;++m)exact+=exp(-beta*ww[m]);
            double fast=(1+exp(-beta))*total/2+(1-exp(-beta))*a[c]/2;
            assert(abs(exact-fast)<1e-10);
        }
    }
    cout<<"PASS: Walsh replacement energies equal direct enumeration (1600 cases)\n";
    return 0;
}
