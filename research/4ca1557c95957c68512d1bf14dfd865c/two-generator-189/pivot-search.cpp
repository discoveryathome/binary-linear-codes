// Exhaust the fixed parent neighborhood in nonzero field-scalar coordinates.
#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

using U = uint64_t;
struct Word { U a=0,b=0,c=0; };
using Genome = std::array<unsigned,6>;
const U M=(U(1)<<63)|1, MASK=(U(1)<<63)-1;
const std::array<U,9> FACTORS={0x43,0x49,0x57,0x5b,0x61,0x67,0x6d,0x73,0x75};

unsigned degree(U a) { return 63-__builtin_clzll(a); }
std::pair<U,U> divide(U a,U b) {
    if(!b) throw std::runtime_error("zero divisor");
    U q=0;
    while(a && degree(a)>=degree(b)) {
        unsigned j=degree(a)-degree(b); q^=U(1)<<j; a^=b<<j;
    }
    return {q,a};
}
U multiply(U a,U b) {
    U r=0;
    while(b) { if(b&1) r^=a; a<<=1; b>>=1; }
    return r;
}
Word encode(U a,U b,U c) {
    if((a|b|c)&~MASK) throw std::runtime_error("63-bit block");
    return {a|((b&1)<<63),(b>>1)|((c&3)<<62),c>>2};
}
struct Fitness { bool exact; unsigned d,count,message; };
Fitness evaluate(const std::vector<Word>& rows,unsigned cutoff) {
    if(rows.empty() || rows.size()>22) throw std::runtime_error("enumeration cap");
    Word w; Fitness best{true,190,0,0};
    for(unsigned i=1;i<(1u<<rows.size());++i) {
        const Word& r=rows[__builtin_ctz(i)]; w.a^=r.a;w.b^=r.b;w.c^=r.c;
        unsigned weight=__builtin_popcountll(w.a)+__builtin_popcountll(w.b)+__builtin_popcountll(w.c);
        unsigned message=i^(i>>1);
        if(weight<cutoff) return {false,weight,0,message};
        if(weight<best.d) best={true,weight,1,message};
        else if(weight==best.d) ++best.count;
    }
    return best;
}

using Genome=std::array<unsigned,6>;
U pack(const Genome& g) { U n=0;for(unsigned i=0;i<6;++i)n|=U(g[i])<<(6*i);return n; }
std::vector<Word> parent_rows(U three,const std::array<U,3>& factors,const Genome& scalars) {
    if(three!=0xb && three!=0xd)throw std::runtime_error("degree-three factor");
    U g1=divide(M,3).first,g3=divide(M,three).first;
    std::vector<Word> rows{encode(g1,g1,g1)};
    for(unsigned j=0;j<3;++j)rows.push_back(encode(g3<<j,g3<<j,g3<<j));
    for(unsigned i=0;i<3;++i) {
        if(std::find(FACTORS.begin(),FACTORS.end(),factors[i])==FACTORS.end())
            throw std::runtime_error("degree-six factor");
        for(unsigned h=0;h<i;++h)if(factors[h]==factors[i])throw std::runtime_error("repeated factor");
        if(!scalars[2*i]||scalars[2*i]>=64||!scalars[2*i+1]||scalars[2*i+1]>=64)
            throw std::runtime_error("nonzero scalar");
        U generator=divide(M,factors[i]).first;
        for(unsigned j=0;j<6;++j) {
            U a=U(1)<<j;
            rows.push_back(encode(multiply(generator,a),
                multiply(generator,divide(multiply(a,scalars[2*i]),factors[i]).second),
                multiply(generator,divide(multiply(a,scalars[2*i+1]),factors[i]).second)));
        }
    }
    return rows;
}
int main(int argc,char** argv) {
    try {
        if(argc!=7)throw std::runtime_error("usage: OUTPUT_OR_--emit DEGREE3 P1 P2 P3 PACKED_PARENT");
        U three=std::stoull(argv[2]);std::array<U,3> factors;
        for(unsigned i=0;i<3;++i)factors[i]=std::stoull(argv[3+i]);
        U encoded=std::stoull(argv[6]);if(encoded>=(U(1)<<36))throw std::runtime_error("packed scalar range");
        Genome parent;for(unsigned i=0;i<6;++i)parent[i]=(encoded>>(6*i))&63;
        if(std::string(argv[1])=="--emit") {
            for(const Word& r:parent_rows(three,factors,parent))
                std::cout<<std::hex<<r.a<<' '<<r.b<<' '<<r.c<<'\n';
            return 0;
        }
        std::filesystem::path output(argv[1]);
        if(!std::filesystem::is_directory(output)||std::filesystem::exists(output/"ledger.csv"))
            throw std::runtime_error("new output directory required");
        std::vector<Genome> choices{parent};
        for(unsigned i=0;i<6;++i)for(unsigned a=1;a<64;++a)if(a!=parent[i]) {
            Genome g=parent;g[i]=a;choices.push_back(g);
        }
        for(unsigned i=0;i<6;++i)for(unsigned j=i+1;j<6;++j)
            for(unsigned a=1;a<64;++a)if(a!=parent[i])
                for(unsigned b=1;b<64;++b)if(b!=parent[j]) {
                    Genome g=parent;g[i]=a;g[j]=b;choices.push_back(g);
                }
        if(choices.size()!=58033)throw std::runtime_error("neighborhood cardinality");
        std::ofstream ledger(output/"ledger.csv");
        ledger<<"index,genome,changes,message,weight,exact,minimum_words\n";
        unsigned count=0,maxw=0;bool found=false;U candidate=0;
        for(const Genome& genome:choices) {
            Fitness f=evaluate(parent_rows(three,factors,genome),73);
            unsigned changes=0;for(unsigned j=0;j<6;++j)changes+=genome[j]!=parent[j];
            ledger<<count<<','<<pack(genome)<<','<<changes<<','<<f.message<<','<<f.d
                  <<','<<f.exact<<','<<f.count<<'\n';
            ++count;maxw=std::max(maxw,f.d);
            if(f.exact) {found=true;candidate=pack(genome);break;}
            if(count%10000==0) {ledger.flush();std::cout<<"{\"evaluated\":"<<count<<"}\n"<<std::flush;}
        }
        ledger.close();if(!ledger)throw std::runtime_error("ledger write");
        std::ofstream summary(output/"summary.json");
        summary<<"{\"domain_size\":58033,\"evaluated\":"<<count<<",\"target_found\":"
               <<(found?"true":"false")<<",\"candidate_genome\":"<<candidate
               <<",\"maximum_witness\":"<<maxw<<"}\n";
        summary.close();if(!summary)throw std::runtime_error("summary write");
        std::cout<<"{\"status\":\"complete\",\"evaluated\":"<<count<<",\"target_found\":"
                 <<(found?"true":"false")<<",\"maximum_witness\":"<<maxw<<"}\n";
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}

