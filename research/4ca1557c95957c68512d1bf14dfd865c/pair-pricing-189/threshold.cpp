// Rank-16 threshold pricing; Gray/CRT mechanics adapted from this session's PR #12.
#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using U = uint64_t;
struct Word { U a=0,b=0,c=0; };
const U M=(U(1)<<63)|1, MASK=(U(1)<<63)-1;
const std::array<unsigned,9> FACTORS={0x43,0x49,0x57,0x5b,0x61,0x67,0x6d,0x73,0x75};

unsigned degree(U a) { return 63-__builtin_clzll(a); }
std::pair<U,U> divide(U a,U b) {
    if(!b) throw std::runtime_error("zero divisor");
    U q=0;
    while(a && degree(a)>=degree(b)) {
        unsigned j=degree(a)-degree(b);q^=U(1)<<j;a^=b<<j;
    }
    return {q,a};
}
U multiply(U a,U b) {
    U r=0;
    while(b) {if(b&1)r^=a;a<<=1;b>>=1;}
    return r;
}
Word word(U a,U b,U c) {
    if((a|b|c)&~MASK) throw std::runtime_error("block size");
    return {a|((b&1)<<63),(b>>1)|((c&3)<<62),c>>2};
}
std::vector<unsigned> representatives(unsigned p,unsigned q) {
    std::array<bool,4096> seen{};std::vector<unsigned> result;
    for(unsigned start=65;start<4096;++start) {
        if(!(start&63) || seen[start]) continue;
        unsigned value=start;
        do {
            if(seen[value] || !(value&63) || !(value>>6))
                throw std::runtime_error("orbit collision");
            seen[value]=true;
            value=divide(U(value&63)<<3,p).second |
                  (divide(U(value>>6)<<3,q).second<<6);
        } while(value!=start);
        result.push_back(start);
    }
    unsigned count=0;for(bool value:seen) count+=value;
    if(count!=3969) throw std::runtime_error("orbit coverage");
    return result;
}
std::vector<Word> construct(char profile,unsigned p,unsigned q,unsigned f,unsigned g) {
    if((profile!='B' && profile!='C') || p>=q ||
       std::find(FACTORS.begin(),FACTORS.end(),p)==FACTORS.end() ||
       std::find(FACTORS.begin(),FACTORS.end(),q)==FACTORS.end())
        throw std::runtime_error("profile/factors");
    for(unsigned value:{f&63,f>>6,g&63,g>>6})
        if(!value || value>=64) throw std::runtime_error("nonzero scalars");
    U g1=divide(M,3).first,g2=divide(M,7).first;
    std::vector<Word> rows;
    if(profile=='B') {
        for(unsigned j=0;j<2;++j)rows.push_back(word(g2<<j,0,g2<<j));
        for(unsigned j=0;j<2;++j)rows.push_back(word(0,g2<<j,g2<<j));
    } else {
        rows.push_back(word(g1,0,g1));rows.push_back(word(0,g1,g1));
        for(unsigned j=0;j<2;++j)rows.push_back(word(g2<<j,g2<<j,g2<<j));
    }
    for(unsigned i=0;i<2;++i) {
        unsigned factor=i?q:p;U generator=divide(M,factor).first;
        for(unsigned j=0;j<6;++j) {
            U a=U(1)<<j;
            rows.push_back(word(multiply(generator,a),
                multiply(generator,divide(multiply(a,(f>>(6*i))&63),factor).second),
                multiply(generator,divide(multiply(a,(g>>(6*i))&63),factor).second)));
        }
    }
    return rows;
}
struct Result { bool exact;unsigned d,count,message; };
Result evaluate(const std::vector<Word>& rows,unsigned cutoff) {
    if(rows.size()!=16) throw std::runtime_error("rank-16 row count");
    Word w;Result best{true,190,0,0};
    for(unsigned i=1;i<65536;++i) {
        const Word& r=rows[__builtin_ctz(i)];w.a^=r.a;w.b^=r.b;w.c^=r.c;
        unsigned weight=__builtin_popcountll(w.a)+__builtin_popcountll(w.b)+__builtin_popcountll(w.c);
        unsigned message=i^(i>>1);
        if(weight<cutoff)return {false,weight,0,message};
        if(weight<best.d)best={true,weight,1,message};
        else if(weight==best.d)++best.count;
    }
    return best;
}

int main(int argc,char** argv) {
    try {
        if(argc==7 && std::string(argv[1])=="--emit") {
            for(const Word& r:construct(argv[2][0],std::stoul(argv[3]),std::stoul(argv[4]),
                                       std::stoul(argv[5]),std::stoul(argv[6])))
                std::cout<<std::hex<<r.a<<' '<<r.b<<' '<<r.c<<'\n';
            return 0;
        }
        if(argc==3 && std::string(argv[1])=="--check") {
            std::ifstream input(argv[2]);unsigned k;input>>k;
            if(!input || k!=16)throw std::runtime_error("control header");
            std::vector<Word> rows(k);
            for(auto& r:rows)input>>std::hex>>r.a>>r.b>>r.c;
            if(!input)throw std::runtime_error("control data");
            Result r=evaluate(rows,0);
            std::cout<<"{\"d\":"<<r.d<<",\"minimum_words\":"<<r.count<<"}\n";
            return 0;
        }
        if(argc!=3 || std::string(argv[1])!="--search")
            throw std::runtime_error("usage: --emit PROFILE P Q F G | --check FILE | --search NEW_OUTPUT");
        std::filesystem::path output(argv[2]);
        if(!std::filesystem::is_directory(output) || std::filesystem::exists(output/"ledger.csv"))
            throw std::runtime_error("new output required");
        std::ofstream ledger(output/"ledger.csv"),summary(output/"cases.json");
        if(!ledger || !summary)throw std::runtime_error("output open");
        ledger<<"case,index,f_pair,g_pair,exact,d_or_upper,minimum_words,message\n";
        summary<<'[';unsigned case_id=0,total=0,survivors=0;
        for(char profile:{'B','C'})for(unsigned i=0;i<8;++i)for(unsigned j=i+1;j<9;++j) {
            unsigned p=FACTORS[i],q=FACTORS[j];auto reps=representatives(p,q);
            unsigned index=0;bool found=false;
            for(unsigned f:reps) {
                for(unsigned g:reps) {
                    Result r=evaluate(construct(profile,p,q,f,g),74);
                    ledger<<case_id<<','<<index<<','<<f<<','<<g<<','<<r.exact<<','
                          <<r.d<<','<<r.count<<','<<r.message<<'\n';
                    ++index;++total;
                    if(r.exact) {found=true;break;}
                }
                if(found)break;
            }
            if(case_id)summary<<',';
            summary<<"{\"case\":"<<case_id<<",\"profile\":\""<<profile
                   <<"\",\"factors\":["<<p<<','<<q<<"],\"orbit_representatives\":"<<reps.size()
                   <<",\"domain\":"<<reps.size()*reps.size()<<",\"tested\":"<<index
                   <<",\"survivor\":"<<(found?"true":"false")<<'}';
            survivors+=found;++case_id;
        }
        summary<<"]\n";ledger.close();summary.close();
        if(!ledger || !summary || case_id!=72)throw std::runtime_error("write/completeness");
        std::cout<<"{\"cases\":"<<case_id<<",\"tested\":"<<total
                 <<",\"surviving_pairs\":"<<survivors<<"}\n";
        return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
