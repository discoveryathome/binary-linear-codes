// Complete conservative pair filtering and full-code join; adapted from PRs #12/#13.
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
    if(rows.size()!=16 && rows.size()!=22) throw std::runtime_error("row count");
    Word w;Result best{true,190,0,0};
    for(unsigned i=1;i<(1u<<rows.size());++i) {
        const Word& r=rows[__builtin_ctz(i)];w.a^=r.a;w.b^=r.b;w.c^=r.c;
        unsigned weight=__builtin_popcountll(w.a)+__builtin_popcountll(w.b)+__builtin_popcountll(w.c);
        unsigned message=i^(i>>1);
        if(weight<cutoff)return {false,weight,0,message};
        if(weight<best.d)best={true,weight,1,message};
        else if(weight==best.d)++best.count;
    }
    return best;
}

using Scalars = std::array<unsigned,6>;
using Bits = std::array<U,63>;
using Relation = std::vector<Bits>;
const unsigned CAP=2000000;
struct Table {
    unsigned i,j;char profile;std::vector<unsigned> reps;
    std::vector<uint16_t> messages;std::vector<uint8_t> weights;
    unsigned allowed=0;
};
unsigned rotate_pair(unsigned value,unsigned p,unsigned q) {
    return divide(U(value&63)<<3,p).second | (divide(U(value>>6)<<3,q).second<<6);
}
std::vector<unsigned> orbit(unsigned value,unsigned p,unsigned q) {
    std::vector<unsigned> values;unsigned start=value;
    do {values.push_back(value);value=rotate_pair(value,p,q);}while(value!=start);
    return values;
}
unsigned state(unsigned f,unsigned g) {return (f-1)*63+g-1;}
std::vector<unsigned> root_reps(unsigned factor) {
    std::array<bool,64> seen{};std::vector<unsigned> result;
    for(unsigned start=1;start<64;++start)if(!seen[start]) {
        unsigned value=start,count=0;
        do {seen[value]=true;++count;value=divide(U(value)<<3,factor).second;}while(value!=start);
        if(count!=21)throw std::runtime_error("primitive root period");
        result.push_back(start);
    }
    if(result.size()!=3)throw std::runtime_error("primitive root orbit count");
    return result;
}
std::vector<Word> full_rows(char profile,const std::array<unsigned,3>& factors,const Scalars& s) {
    auto rows=construct(profile,factors[0],factors[1],s[0]|(s[2]<<6),s[1]|(s[3]<<6));
    unsigned p=factors[2];U generator=divide(M,p).first;
    if(std::find(FACTORS.begin(),FACTORS.end(),p)==FACTORS.end() || p<=factors[1])
        throw std::runtime_error("third factor");
    for(unsigned value:{s[4],s[5]})if(!value || value>=64)throw std::runtime_error("third scalars");
    for(unsigned j=0;j<6;++j) {
        U a=U(1)<<j;
        rows.push_back(word(multiply(generator,a),
            multiply(generator,divide(multiply(a,s[4]),p).second),
            multiply(generator,divide(multiply(a,s[5]),p).second)));
    }
    return rows;
}
U pack(const Scalars& s) {U value=0;for(unsigned i=0;i<6;++i)value|=U(s[i])<<(6*i);return value;}

int main(int argc,char** argv) {
    try {
        if(argc==7 && std::string(argv[1])=="--emit") {
            for(const Word& r:construct(argv[2][0],std::stoul(argv[3]),std::stoul(argv[4]),
                                       std::stoul(argv[5]),std::stoul(argv[6])))
                std::cout<<std::hex<<r.a<<' '<<r.b<<' '<<r.c<<'\n';
            return 0;
        }
        if(argc==12 && std::string(argv[1])=="--emit-full") {
            std::array<unsigned,3> factors;Scalars s;
            for(unsigned i=0;i<3;++i)factors[i]=std::stoul(argv[3+i]);
            for(unsigned i=0;i<6;++i)s[i]=std::stoul(argv[6+i]);
            for(const Word& r:full_rows(argv[2][0],factors,s))
                std::cout<<std::hex<<r.a<<' '<<r.b<<' '<<r.c<<'\n';
            return 0;
        }
        if(argc==3 && std::string(argv[1])=="--check") {
            std::ifstream input(argv[2]);unsigned k;input>>k;
            if(!input || (k!=16 && k!=22))throw std::runtime_error("control header");
            std::vector<Word> rows(k);
            for(auto& r:rows)input>>std::hex>>r.a>>r.b>>r.c;
            if(!input)throw std::runtime_error("control data");
            Result r=evaluate(rows,0);
            std::cout<<"{\"d\":"<<r.d<<",\"minimum_words\":"<<r.count<<"}\n";
            return 0;
        }
        if(argc!=3 || std::string(argv[1])!="--run")throw std::runtime_error("use --run NEW_OUTPUT");
        std::filesystem::path output(argv[2]);
        if(!std::filesystem::is_directory(output) || std::filesystem::exists(output/"pair-witnesses.bin"))
            throw std::runtime_error("new output required");
        std::ofstream raw(output/"pair-witnesses.bin",std::ios::binary),pair_json(output/"pairs.json");
        if(!raw || !pair_json)throw std::runtime_error("pair output open");
        std::vector<Table> tables;unsigned pair_total=0,allowed_total=0;pair_json<<'[';
        for(char profile:{'B','C'})for(unsigned i=0;i<8;++i)for(unsigned j=i+1;j<9;++j) {
            Table table{i,j,profile,representatives(FACTORS[i],FACTORS[j]),{},{},0};
            for(unsigned f:table.reps)for(unsigned g:table.reps) {
                Result r=evaluate(construct(profile,FACTORS[i],FACTORS[j],f,g),74);
                unsigned message=r.exact?0:r.message,weight=r.exact?0:r.d;
                if(message>=65536 || weight>=74)throw std::runtime_error("pair witness encoding");
                table.messages.push_back(message);table.weights.push_back(weight);
                raw.put(message&255);raw.put((message>>8)&255);raw.put(weight);
                table.allowed+=r.exact;++pair_total;
            }
            if(!tables.empty())pair_json<<',';
            pair_json<<"{\"case\":"<<tables.size()<<",\"profile\":\""<<profile
                     <<"\",\"factors\":["<<FACTORS[i]<<','<<FACTORS[j]<<"],\"representatives\":"
                     <<table.reps.size()<<",\"domain\":"<<table.messages.size()
                     <<",\"allowed\":"<<table.allowed<<'}';
            allowed_total+=table.allowed;tables.push_back(std::move(table));
        }
        raw.close();pair_json<<"]\n";pair_json.close();
        if(!raw || !pair_json || pair_total!=3143448)throw std::runtime_error("pair write/count");
        std::cout<<"{\"pair_choices\":"<<pair_total<<",\"allowed\":"<<allowed_total<<"}\n"<<std::flush;
        std::ofstream ledger(output/"full-ledger.csv"),cases(output/"triples.json");
        if(!ledger || !cases)throw std::runtime_error("full output open");
        ledger<<"template,index,scalars,message,d_or_upper,exact,minimum_words\n";
        cases<<'[';unsigned template_id=0,checked=0;bool stopped=false,target=false;
        for(unsigned profile_id=0;profile_id<2;++profile_id) {
            char profile=profile_id?'C':'B';
            std::array<std::array<Relation,9>,9> adj;
            for(const Table& table:tables)if(table.profile==profile && table.allowed) {
                unsigned i=table.i,j=table.j,n=table.reps.size();
                adj[i][j]=Relation(3969,Bits{});adj[j][i]=Relation(3969,Bits{});
                for(unsigned index=0;index<table.messages.size();++index)if(!table.messages[index]) {
                    auto fs=orbit(table.reps[index/n],FACTORS[i],FACTORS[j]);
                    auto gs=orbit(table.reps[index%n],FACTORS[i],FACTORS[j]);
                    for(unsigned f:fs)for(unsigned g:gs) {
                        unsigned a=state(f&63,g&63),b=state(f>>6,g>>6);
                        if(adj[i][j][a][b/64]&(U(1)<<(b%64)))throw std::runtime_error("edge duplicate");
                        adj[i][j][a][b/64]|=U(1)<<(b%64);
                        adj[j][i][b][a/64]|=U(1)<<(a%64);
                    }
                }
            }
            for(unsigned i=0;i<7;++i)for(unsigned j=i+1;j<8;++j)for(unsigned k=j+1;k<9;++k) {
                std::array<unsigned,3> indices={i,j,k},factors={FACTORS[i],FACTORS[j],FACTORS[k]};
                unsigned local=0,root=9;bool complete=!stopped;
                bool empty=adj[i][j].empty() || adj[i][k].empty() || adj[j][k].empty();
                if(!empty && !stopped) {
                    for(unsigned v:indices)if(FACTORS[v]!=0x49 && FACTORS[v]!=0x57 && FACTORS[v]!=0x75) {root=v;break;}
                    if(root==9)throw std::runtime_error("nonprimitive triple not pair-excluded");
                    std::vector<unsigned> others;for(unsigned v:indices)if(v!=root)others.push_back(v);
                    unsigned b=others[0],c=others[1];auto roots=root_reps(FACTORS[root]);
                    for(unsigned rf:roots) {
                        for(unsigned rg:roots) {
                            unsigned x=state(rf,rg);
                            for(unsigned limb=0;limb<63 && !stopped;++limb) {
                                U bs=adj[root][b][x][limb];
                                while(bs && !stopped) {
                                    unsigned bit=__builtin_ctzll(bs),y=64*limb+bit;bs&=bs-1;
                                    for(unsigned cl=0;cl<63 && !stopped;++cl) {
                                        U cs=adj[root][c][x][cl]&adj[b][c][y][cl];
                                        while(cs && !stopped) {
                                            unsigned cb=__builtin_ctzll(cs),z=64*cl+cb;cs&=cs-1;
                                            if(checked==CAP) {stopped=true;complete=false;break;}
                                            Scalars s;
                                            for(unsigned a=0;a<3;++a) {
                                                unsigned value=indices[a]==root?x:(indices[a]==b?y:z);
                                                s[2*a]=value/63+1;s[2*a+1]=value%63+1;
                                            }
                                            Result r=evaluate(full_rows(profile,factors,s),74);
                                            ledger<<template_id<<','<<local<<','<<pack(s)<<','<<r.message<<','
                                                  <<r.d<<','<<r.exact<<','<<r.count<<'\n';
                                            ++local;++checked;
                                            if(r.exact) {target=true;stopped=true;complete=false;}
                                        }
                                    }
                                }
                            }
                            if(stopped)break;
                        }
                        if(stopped)break;
                    }
                }
                if(template_id)cases<<',';
                cases<<"{\"template\":"<<template_id<<",\"profile\":\""<<profile
                     <<"\",\"factors\":["<<factors[0]<<','<<factors[1]<<','<<factors[2]
                     <<"],\"root\":"<<(root==9?0:FACTORS[root])<<",\"checked\":"<<local
                     <<",\"complete\":"<<(complete?"true":"false")<<'}';
                ++template_id;
            }
        }
        cases<<"]\n";ledger.close();cases.close();
        if(!ledger || !cases || template_id!=168)throw std::runtime_error("full write/count");
        std::ofstream summary(output/"summary.json");
        summary<<"{\"pair_choices\":"<<pair_total<<",\"pair_allowed\":"<<allowed_total
               <<",\"full_checked\":"<<checked<<",\"complete\":"<<(!stopped?"true":"false")
               <<",\"target_found\":"<<(target?"true":"false")<<",\"cap\":"<<CAP<<"}\n";
        summary.close();if(!summary)throw std::runtime_error("summary write");
        std::cout<<"{\"full_checked\":"<<checked<<",\"complete\":"<<(!stopped?"true":"false")
                 <<",\"target_found\":"<<(target?"true":"false")<<"}\n";
        return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
