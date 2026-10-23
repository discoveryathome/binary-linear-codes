// Exact Gray enumeration for the bounded two-generator CRT experiment.
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
bool better(const Fitness& a,const Fitness& b) {
    return a.d>b.d || (a.d==b.d && a.count<b.count);
}
std::vector<Word> construct(char profile,const std::array<U,3>& factors,const Genome& s) {
    if(profile!='B' && profile!='C') throw std::runtime_error("profile");
    for(unsigned value:s) if(!value || value>=64) throw std::runtime_error("unit scalar");
    for(unsigned i=0;i<3;++i) {
        if(std::find(FACTORS.begin(),FACTORS.end(),factors[i])==FACTORS.end())
            throw std::runtime_error("factor");
        for(unsigned j=0;j<i;++j) if(factors[i]==factors[j]) throw std::runtime_error("repeated factor");
    }
    U g1=divide(M,3).first,g2=divide(M,7).first;
    std::vector<Word> rows;
    if(profile=='B') {
        for(unsigned j=0;j<2;++j) rows.push_back(encode(g2<<j,0,g2<<j));
        for(unsigned j=0;j<2;++j) rows.push_back(encode(0,g2<<j,g2<<j));
    } else {
        rows.push_back(encode(g1,0,g1));rows.push_back(encode(0,g1,g1));
        for(unsigned j=0;j<2;++j) rows.push_back(encode(g2<<j,g2<<j,g2<<j));
    }
    for(unsigned i=0;i<3;++i) {
        U p=factors[i],generator=divide(M,p).first;
        for(unsigned j=0;j<6;++j) {
            U a=U(1)<<j;
            rows.push_back(encode(multiply(generator,a),
                multiply(generator,divide(multiply(a,s[2*i]),p).second),
                multiply(generator,divide(multiply(a,s[2*i+1]),p).second)));
        }
    }
    return rows;
}
U pack(const Genome& g) {
    U value=0;for(unsigned i=0;i<6;++i) value|=U(g[i])<<(6*i);return value;
}
struct Random {
    U state;
    U next() { state^=state>>12;state^=state<<25;state^=state>>27;return state*2685821657736338717ULL; }
    unsigned below(unsigned n) { return next()%n; }
    Genome genome() { Genome g;for(auto& value:g) value=1+below(63);return g; }
    Genome mutate(Genome g) {
        unsigned count=1+below(3),used=0;
        for(unsigned i=0;i<count;++i) {
            unsigned slot;do {slot=below(6);} while(used&(1u<<slot));used|=1u<<slot;
            unsigned value;do {value=1+below(63);} while(value==g[slot]);g[slot]=value;
        }
        return g;
    }
};
struct Template {
    char profile;std::array<U,3> factors;Genome best_genome{};
    Fitness best{true,0,~0u,0};
};
void genome_json(std::ostream& out,const Genome& g) {
    out<<'[';for(unsigned i=0;i<6;++i) {if(i)out<<',';out<<g[i];}out<<']';
}
void factors_json(std::ostream& out,const std::array<U,3>& f) {
    out<<'['<<f[0]<<','<<f[1]<<','<<f[2]<<']';
}

int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--check") {
            std::ifstream input(argv[2]);unsigned k;input>>k;
            if(!input || k==0 || k>22) throw std::runtime_error("control header");
            std::vector<Word> rows(k);
            for(auto& r:rows) input>>std::hex>>r.a>>r.b>>r.c;
            if(!input) throw std::runtime_error("control rows");
            Fitness f=evaluate(rows,0);
            std::cout<<"{\"d\":"<<f.d<<",\"minimum_words\":"<<f.count
                     <<",\"message\":"<<f.message<<"}\n";return 0;
        }
        if(argc==12 && std::string(argv[1])=="--emit") {
            std::array<U,3> factors;Genome s;
            for(unsigned i=0;i<3;++i) factors[i]=std::stoull(argv[3+i],nullptr,0);
            for(unsigned i=0;i<6;++i) s[i]=std::stoul(argv[6+i]);
            for(const Word& r:construct(argv[2][0],factors,s))
                std::cout<<std::hex<<r.a<<' '<<r.b<<' '<<r.c<<'\n';
            return 0;
        }
        if(argc!=4 || std::string(argv[1])!="--search")
            throw std::runtime_error("usage: --check FILE | --emit PROFILE FACTORS SCALARS | --search NEW_OUTPUT SEED64");
        std::filesystem::path output(argv[2]);
        if(!std::filesystem::is_directory(output) || std::filesystem::exists(output/"ledger.csv"))
            throw std::runtime_error("new output directory required");
        U initial_seed=std::stoull(argv[3]);
        if(!initial_seed) throw std::runtime_error("nonzero PRNG state");
        Random random{initial_seed};std::vector<Template> templates;
        for(char profile:{'B','C'}) for(unsigned i=0;i<7;++i)
            for(unsigned j=i+1;j<8;++j) for(unsigned k=j+1;k<9;++k)
                templates.push_back({profile,{FACTORS[i],FACTORS[j],FACTORS[k]}});
        if(templates.size()!=168) throw std::runtime_error("template count");
        std::ofstream ledger(output/"ledger.csv");
        if(!ledger) throw std::runtime_error("ledger open");
        ledger<<"index,template,stage,restart,step,genome,duplicate,exact,d_or_upper,minimum_words,message,accepted\n";
        std::unordered_set<U> seen;U proposals=0,duplicates=0;unsigned global=0;
        bool target=false;std::vector<unsigned> selected;
        auto record=[&](unsigned t,unsigned stage,int restart,unsigned step,const Genome& g,
                        const Fitness& f,bool accepted) {
            U encoded=pack(g),key=(U(t)<<36)|encoded;bool duplicate=!seen.insert(key).second;
            duplicates+=duplicate;
            ledger<<proposals<<','<<t<<','<<stage<<','<<restart<<','<<step<<','<<encoded<<','
                  <<duplicate<<','<<f.exact<<','<<f.d<<','<<f.count<<','<<f.message<<','<<accepted<<'\n';
            ++proposals;
            if(f.exact && better(f,templates[t].best)) {templates[t].best=f;templates[t].best_genome=g;}
            if(better(templates[t].best,templates[global].best)) global=t;
            if(templates[global].best.d>=73) target=true;
            if(proposals%20000==0) {
                ledger.flush();std::cout<<"{\"proposals\":"<<proposals<<",\"best_d\":"
                    <<templates[global].best.d<<"}\n"<<std::flush;
            }
        };
        for(unsigned t=0;t<templates.size() && !target;++t) for(unsigned s=0;s<16 && !target;++s) {
            Genome g=random.genome();Fitness f=evaluate(construct(templates[t].profile,templates[t].factors,g),0);
            bool accepted=better(f,templates[t].best);record(t,0,-1,s,g,f,accepted);
        }
        if(!target) {
            selected.resize(templates.size());std::iota(selected.begin(),selected.end(),0);
            std::stable_sort(selected.begin(),selected.end(),[&](unsigned a,unsigned b){
                return better(templates[a].best,templates[b].best);});selected.resize(16);
            std::cout<<"{\"initial_complete\":"<<proposals<<",\"best_d\":"
                     <<templates[global].best.d<<"}\n"<<std::flush;
            for(unsigned t:selected) {
                if(target)break;
                for(unsigned restart=0;restart<3 && !target;++restart) {
                    Genome current=templates[t].best_genome;Fitness fitness=templates[t].best;
                    for(unsigned step=0;step<4096 && !target;++step) {
                        bool fresh=restart>0 && step==0;
                        Genome proposed=fresh?random.genome():random.mutate(current);
                        Fitness f=evaluate(construct(templates[t].profile,templates[t].factors,proposed),fresh?0:fitness.d);
                        bool accepted=f.exact && (fresh || better(f,fitness) ||
                            (f.d==fitness.d && f.count==fitness.count && random.below(8)==0));
                        if(accepted) {current=proposed;fitness=f;}
                        record(t,1,restart,step,proposed,f,accepted);
                    }
                }
            }
        }
        ledger.close();if(!ledger)throw std::runtime_error("ledger write");
        std::ofstream summary(output/"summary.json");
        summary<<"{\"seed64\":"<<initial_seed<<",\"proposals\":"<<proposals
               <<",\"duplicates\":"<<duplicates<<",\"target_found\":"<<(target?"true":"false")
               <<",\"best_template\":"<<global<<",\"selected_templates\":[";
        for(unsigned i=0;i<selected.size();++i){if(i)summary<<',';summary<<selected[i];}
        summary<<"],\"templates\":[";
        for(unsigned i=0;i<templates.size();++i) {
            const auto& t=templates[i];if(i)summary<<',';
            summary<<"{\"profile\":\""<<t.profile<<"\",\"factors\":";factors_json(summary,t.factors);
            summary<<",\"scalars\":";genome_json(summary,t.best_genome);
            summary<<",\"d\":"<<t.best.d<<",\"minimum_words\":"<<t.best.count
                   <<",\"message\":"<<t.best.message<<'}';
        }
        summary<<"]}\n";summary.close();if(!summary)throw std::runtime_error("summary write");
        std::cout<<"{\"status\":\"complete\",\"proposals\":"<<proposals<<",\"duplicates\":"
                 <<duplicates<<",\"best_d\":"<<templates[global].best.d
                 <<",\"target_found\":"<<(target?"true":"false")<<"}\n";
        return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
