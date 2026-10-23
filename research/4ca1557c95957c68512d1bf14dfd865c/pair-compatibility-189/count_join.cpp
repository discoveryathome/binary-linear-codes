// Separate count-only audit: GF(64) shifts, expanded relations and population counts.
// This file imports no primary source and performs no full-code distance evaluations.
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <vector>

using U=uint64_t;
using Row=std::array<U,63>;
using Matrix=std::vector<Row>;
const std::array<unsigned,9> F={67,73,87,91,97,103,109,115,117};

unsigned advance(unsigned symbol,unsigned polynomial) {
    for(unsigned j=0;j<3;++j) {
        symbol<<=1;
        if(symbol&64)symbol^=polynomial;
    }
    if(!symbol || symbol>=64)throw std::runtime_error("field action");
    return symbol;
}
std::map<unsigned,std::vector<unsigned>> pair_orbits(unsigned p,unsigned q) {
    std::array<bool,4096> used{};
    std::map<unsigned,std::vector<unsigned>> result;
    unsigned covered=0;
    for(unsigned start=65;start<4096;++start)if((start&63) && !used[start]) {
        unsigned value=start;
        auto& orbit=result[start];
        do {
            if(used[value])throw std::runtime_error("pair orbit collision");
            used[value]=true;++covered;orbit.push_back(value);
            value=advance(value&63,p)|(advance(value>>6,q)<<6);
        }while(value!=start);
    }
    unsigned expected=(p==87 && q==117)?567:189;
    if(covered!=3969 || result.size()!=expected)throw std::runtime_error("pair coverage");
    return result;
}
std::vector<unsigned> root_orbits(unsigned p) {
    std::array<bool,64> used{};std::vector<unsigned> roots;
    for(unsigned start=1;start<64;++start)if(!used[start]) {
        unsigned value=start,count=0;roots.push_back(start);
        do {used[value]=true;++count;value=advance(value,p);}while(value!=start);
        if(count!=21)throw std::runtime_error("root period");
    }
    if(roots.size()!=3)throw std::runtime_error("root coverage");
    return roots;
}
unsigned state(unsigned f,unsigned g) {return (f-1)*63+g-1;}

int main(int argc,char** argv) {
    try {
        if(argc!=3 || std::filesystem::exists(argv[2]))throw std::runtime_error("use RAW_PAIR_DATA NEW_REPORT");
        std::ifstream input(argv[1],std::ios::binary);
        if(!input)throw std::runtime_error("pair input");
        std::ofstream output(argv[2]);
        if(!output)throw std::runtime_error("report output");
        U grand=0;std::array<U,2> totals{};unsigned template_id=0,entries=0;
        output<<"{\"templates\":[";
        for(unsigned profile=0;profile<2;++profile) {
            std::array<std::array<Matrix,9>,9> graph;
            for(unsigned i=0;i<8;++i)for(unsigned j=i+1;j<9;++j) {
                auto orbits=pair_orbits(F[i],F[j]);
                bool initialized=false;
                for(const auto& f:orbits)for(const auto& g:orbits) {
                    int a=input.get(),b=input.get(),weight=input.get();
                    if(a<0 || b<0 || weight<0)throw std::runtime_error("short pair data");
                    ++entries;unsigned message=a|(b<<8);
                    if(message)continue;
                    if(weight)throw std::runtime_error("allowed marker");
                    if(!initialized) {
                        graph[i][j]=Matrix(3969,Row{});graph[j][i]=Matrix(3969,Row{});
                        initialized=true;
                    }
                    for(unsigned fv:f.second)for(unsigned gv:g.second) {
                        unsigned x=state(fv&63,gv&63),y=state(fv>>6,gv>>6);
                        if(graph[i][j][x][y/64]&(U(1)<<(y%64)))throw std::runtime_error("duplicate edge");
                        graph[i][j][x][y/64]|=U(1)<<(y%64);
                        graph[j][i][y][x/64]|=U(1)<<(x%64);
                    }
                }
            }
            for(unsigned i=0;i<7;++i)for(unsigned j=i+1;j<8;++j)for(unsigned k=j+1;k<9;++k) {
                U count=0;
                if(!graph[i][j].empty() && !graph[i][k].empty() && !graph[j][k].empty()) {
                    std::array<unsigned,3> vertices={i,j,k};unsigned root=9;
                    for(unsigned v:vertices)if(F[v]!=73 && F[v]!=87 && F[v]!=117) {root=v;break;}
                    if(root==9)throw std::runtime_error("nonprimitive surviving triple");
                    std::vector<unsigned> others;for(unsigned v:vertices)if(v!=root)others.push_back(v);
                    unsigned b=others[0],c=others[1];auto reps=root_orbits(F[root]);
                    for(unsigned f:reps)for(unsigned g:reps) {
                        unsigned x=state(f,g);
                        for(unsigned limb=0;limb<63;++limb) {
                            U neighbors=graph[root][b][x][limb];
                            while(neighbors) {
                                unsigned y=64*limb+__builtin_ctzll(neighbors);neighbors&=neighbors-1;
                                for(unsigned z=0;z<63;++z)
                                    count+=__builtin_popcountll(graph[root][c][x][z]&graph[b][c][y][z]);
                            }
                        }
                    }
                }
                if(template_id)output<<',';
                output<<"{\"template\":"<<template_id<<",\"allowed_join\":"<<count<<'}';
                ++template_id;totals[profile]+=count;
            }
            grand+=totals[profile];
        }
        if(entries!=3143448 || input.get()!=EOF || template_id!=168)throw std::runtime_error("input/domain coverage");
        output<<"],\"allowed_join\":"<<grand<<",\"by_profile\":{\"B\":"<<totals[0]
              <<",\"C\":"<<totals[1]<<"}}\n";
        output.close();if(!output)throw std::runtime_error("report write");
        std::cout<<"{\"allowed_join\":"<<grand<<",\"B\":"<<totals[0]<<",\"C\":"<<totals[1]<<"}\n";
        return 0;
    }catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
