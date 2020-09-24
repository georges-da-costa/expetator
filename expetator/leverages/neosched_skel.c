/*******************************************************
 Copyright (C) 2018-2019 Georges Da Costa <georges.da-costa@irit.fr>

    This file is part of Mojitos.

    Mojitos is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Mojitos is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Mojitos.  If not, see <https://www.gnu.org/licenses/>.

*******************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>

#include "neosched_lib.h"

void set_pct(int value) {
  FILE* fid = fopen("/sys/devices/system/cpu/intel_pstate/max_perf_pct", "w");
  fprintf(fid, "%d", value);
  fclose(fid);
}
char **freq_filenames;
void init_dvfs() {
  int res = 0;
  int nb_cores = 0;
  char buffer[100];
  while(res == 0) {
    nb_cores++;
    sprintf(buffer, "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_max_freq", nb_cores);
    res = access(buffer, W_OK);
  }
  freq_filenames = malloc(sizeof(char*)*(nb_cores+1));
  for(int i=0; i<nb_cores; i++) {
    freq_filenames[i] = malloc(sizeof(char)*100);
    sprintf(freq_filenames[i], "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_max_freq", i);
  }
  freq_filenames[nb_cores]=0;
}

void set_freq(int value) {
  for(int i=0; freq_filenames[i]!=0; i++) {
    FILE* fid = fopen(freq_filenames[i], "w");
    fprintf(fid, "%d", value);
    fclose(fid);
  }
}

int freq = -1;
int target = 0;
//                                4          4                   6           10
//void choose_frequency(long long counter, long long network, long rapl, long long system) {

ALGO_FUNC(choose_frequency_rapl) {
  if (new_rapl[2]-old_rapl[2] + new_rapl[5]-old_rapl[5] > 4000000)
    target = 1200000;
  else
    target = 2400000;
  if (target != freq) {
    set_freq(target);
    freq = target;
  }
}

ALGO_FUNC(choose_frequency_network) {
  if (new_network[1]-old_network[1] + new_network[3]-old_network[3] > 20000000)
    target = 1200000;
  else
    target = 2400000;
  if (target != freq) {
    set_freq(target);
    freq = target;
  }
}

ALGO_FUNC(choose_frequency_packet) {
  if (new_network[0]-old_network[0] + new_network[2]-old_network[2] > 10000)
    target = 1200000;
  else
    target = 2400000;
  if (target != freq) {
    set_freq(target);
    freq = target;
  }
}

ALGO_FUNC(choose_frequency_all) {
  if ((new_network[1]-old_network[1] + new_network[3]-old_network[3] > 20000000) || (new_rapl[2]-old_rapl[2] + new_rapl[5]-old_rapl[5] > 3000000) || (new_network[0]-old_network[0] + new_network[2]-old_network[2] > 10000))
    target = 1200000;
  else
    target = 2400000;
  if (target != freq) {
    set_freq(target);
    freq = target;
  }
}

ALGO_FUNC(choose_frequency_none) {
}


ALGO_FUNC(choose_frequency_nopct) {
  int y = 0;

  long long rxp = new_network[0]-old_network[0];
  long long rxb = new_network[1]-old_network[1];
  long long txp = new_network[2]-old_network[2];
  long long txb = new_network[3]-old_network[3];
  
  uint64_t package = new_rapl[0]-old_rapl[0]+new_rapl[3]-old_rapl[3];
  uint64_t dram = new_rapl[2]-old_rapl[2]+new_rapl[5]-old_rapl[5];

  long long user = new_load[0]-old_load[0];
  long long idle = new_load[3]-old_load[3];

  //////////////////////////////
  int frequencies[] = {0, 1200000, 1300000, 2400000};
  if (user <= 111.5) {
   if (rxb <= 95076.5) {
      y = 2;
   }
   else {
      if (freq <= 1650000.0) {
         y = 0;
      }
      else {
         y = 1;
      }
   }
}
else {
   if (idle <= 79.5) {
      if (freq <= 1850000.0) {
         y = 0;
      }
      else {
         y = 1;
      }
   }
   else {
      if (freq <= 2250000.0) {
         y = 3;
      }
      else {
         y = 0;
      }
   }
}

  /////////////////////////////////
  if (y == 0) return;
  target = frequencies[y];
  set_freq(target);
  freq = target;
}



#define ARGUMENTS  {"neosched", "-p", "branch_misses", "-r", "-f", "10", NULL}
#define NBARGUMENTS 6
#define PCT0 pct0
#define PCT1 pct1
#define PCT2 pct2
#define PCT3 pct3

//DEFINE PCT

char * arguments[] = ARGUMENTS;
char **get_argv(int *argc){
  *argc = NBARGUMENTS;
  return arguments;
}


extern FILE* output;
unsigned int global_timer=0;

int frequencies[] = {0};
ALGO_FUNC(choose_frequency_neosched) {
  int y = 0;

  /*  long long PCT0 = counters[0];
  long long PCT1 = counters[1];
  long long PCT2 = counters[2];
  long long PCT3 = counters[3];
  */
  
  long long irxp = new_infiniband[0]-old_infiniband[0];
  long long irxb = new_infiniband[1]-old_infiniband[1];
  long long itxp = new_infiniband[2]-old_infiniband[2];
  long long itxb = new_infiniband[3]-old_infiniband[3];

  long long rxp = new_network[0]-old_network[0];
  long long rxb = new_network[1]-old_network[1];
  long long txp = new_network[2]-old_network[2];
  long long txb = new_network[3]-old_network[3];
  
  uint64_t package00 = new_rapl[0]-old_rapl[0];
  uint64_t package11 = new_rapl[3]-old_rapl[3];
  uint64_t dram0 = new_rapl[2]-old_rapl[2];
  uint64_t dram1 = new_rapl[5]-old_rapl[5];

  long long user = new_load[0]-old_load[0];
  long long nice = new_load[1]-old_load[1];
  long long system = new_load[2]-old_load[2];
  long long idle = new_load[3]-old_load[3];
  long long iowait = new_load[4]-old_load[4];
  long long irq = new_load[5]-old_load[5];
  long long softirq = new_load[6]-old_load[6];
  long long steal = new_load[7]-old_load[7];
  long long guest = new_load[8]-old_load[8];
  long long guest_nice = new_load[9]-old_load[9];

  /////////////////////////////////
  //CORE_LOOP
  /////////////////////////////////

  target = frequencies[y];
  global_timer++;
  if ((target == 0) || target == freq) return;

  fprintf(output, "%u %d %d \n", global_timer, freq, target);
  
  set_freq(target);
  freq = target;
}


