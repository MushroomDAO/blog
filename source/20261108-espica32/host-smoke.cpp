#include <cassert>
#include <fstream>
#include <iostream>
#include <vector>
#include "kiwiadpcm.h"
#include "audiobuf.h"
int main(int argc,char**argv){
 assert(argc==3); std::ifstream input(argv[1],std::ios::binary);std::vector<uint8_t>b((std::istreambuf_iterator<char>(input)),{});assert(!b.empty());std::vector<int16_t>pcm(b.size()*2);ImaAdpcm d;assert(d.decode(b.data(),b.size(),pcm.data())==pcm.size());
 std::ofstream out(argv[2],std::ios::binary);for(auto v:pcm){out.put(v&255);out.put((uint16_t(v)>>8)&255);}out.close();
 ImaAdpcm segmented;std::vector<int16_t>p2(pcm.size());size_t off=0;while(off<b.size()){size_t n=std::min(size_t(137),b.size()-off);segmented.decode(b.data()+off,n,p2.data()+off*2);off+=n;}assert(pcm==p2);d.reset();std::vector<int16_t>again(pcm.size());d.decode(b.data(),b.size(),again.data());assert(again==pcm);
 BufCtl c;assert(c.targetMs(300,true)==300);c.onUnderrun(1,300);assert(c.targetMs(300,true)==600);for(int i=0;i<20;i++)c.onUnderrun(100+i,300);assert(c.targetMs(300,true)==2000);assert(c.targetMs(300,false)==300);c.tick(90120,300);assert(c.autoMs==1900);c.tick(120121,300);assert(c.autoMs==1800);for(int i=0;i<30;i++)c.tick(150122+i*30001,300);assert(c.autoMs==300);
 DriftCtl low;assert(low.decide(0,7200)==1);DriftCtl high;assert(high.decide(13000,7200)==-1);DriftCtl mid;assert(mid.decide(8000,7200)==0);
 std::cout<<"{\"decodedSamples\":"<<pcm.size()<<",\"segmentedMatches\":true,\"resetMatches\":true,\"bufferAndDriftAssertions\":10}"<<std::endl;
}
