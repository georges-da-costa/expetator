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
    along with Foobar.  If not, see <https://www.gnu.org/licenses/>.

 *******************************************************/

#include <stdlib.h>
#include <stdio.h>
#include <asm/unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>
#include <string.h>
#include <getopt.h>
#include <signal.h>

#include "counters.h"
#include "rapl.h"
#include "network.h"
#include "infiniband.h"
#include "load.h"

///////////////////////
#include "neosched_lib.h"
///////////////////////

int rapl_mode=-1;
const int nbzones = 3;
const int rapl_zones[3] = { POWERCAP_RAPL_ZONE_PACKAGE,   POWERCAP_RAPL_ZONE_CORE,   POWERCAP_RAPL_ZONE_DRAM};

#include "counters_option.h"

void show_all_counters() {
  for(int i=0; i<nb_counter_option;i++)
    printf("%s\n", perf_static_info[i].name);
  
}


int nb_perf = 5;
int* perf_indexes=NULL;
// const char* perf_names[5] = {"instructions", "cachemisses", "pagefaults", "branchmisses", "cachmiss"};
// const __u32 perf_type[5] = {PERF_TYPE_HARDWARE,PERF_TYPE_HARDWARE,PERF_TYPE_SOFTWARE, PERF_TYPE_HARDWARE, PERF_TYPE_HW_CACHE};
// const __u64 perf_key[5] = {PERF_COUNT_HW_INSTRUCTIONS, PERF_COUNT_HW_CACHE_MISSES,
//			   PERF_COUNT_SW_PAGE_FAULTS,PERF_COUNT_HW_BRANCH_MISSES,
//			   PERF_COUNT_HW_CACHE_LL};

int perf_mode=-1;
void perf_type_key(__u32 **perf_type, __u64 **perf_key, int *indexes, int nb){
  *perf_type = malloc(nb*sizeof(__u32));
  *perf_key  = malloc(nb*sizeof(__u64));
  for(int i=0; i<nb; i++) {
    (*perf_key)[i]  = perf_static_info[indexes[i]].perf_key;
    (*perf_type)[i] = perf_static_info[indexes[i]].perf_type;
  }
}
void perf_event_list(char *perf_string, int *nb_perf, int **perf_indexes) {
  char *token;
  *nb_perf=0;
  *perf_indexes=NULL;
  char *buffer = malloc(sizeof(char)*(strlen(perf_string)+1));
  strcpy(buffer, perf_string);
  while((token=strtok(buffer, ",")) != NULL) {
    buffer = NULL;
    int i;
    for(i=0; i<nb_counter_option; i++) {
      if(strcmp(perf_static_info[i].name, token) == 0) {
	(*nb_perf)++;
	(*perf_indexes) = realloc(*perf_indexes, sizeof(int)*(*nb_perf));
	(*perf_indexes)[*nb_perf-1]=i;
	break;
      }
    }
    if(i == nb_counter_option) {
      fprintf(stderr, "Unknown performance counter: %s\n", token);
      exit(EXIT_FAILURE);
    }
  }
}

int load_mode = -1;

void usage(char** argv) {
  printf("Usage : %s [-t time] [-f freq] [-r] [-p perf_list] [-l] [-u] [-d network_device] [-i infiniband_path] [-o logfile] [-e command arguments...]\n", argv[0]);
  printf("if time==0 then loops infinitively\n");
  printf("if -e is present, time and freq are not used\n");
  printf("-r activates RAPL\n");
  printf("-p activates performance counters\n");
  printf("   perf_list is coma separated list of performance counters without space. Ex: instructions,cache_misses\n");
  printf("-l lists the possible performance counters and quits\n");
  printf("-d activates network monitoring (if network_device is X, tries to detect it automatically)\n");
  printf("-i activates infiniband monitoring (if infiniband_path is X, tries to detect it automatically)\n");
  printf("-s activates statistics of overhead in nanoseconds\n");
  printf("-u activates report of system load\n");
  exit(EXIT_SUCCESS);
}

void sighandler(int truc) {
}

int stat_mode=-1;

void flush(int truc) {
  exit(0);
}

FILE *output;

void flushexit() {
  fflush(output);
  fclose(output);
}


int main(int argc, char **argv) {
  int total_time=1;
  int delta=0;
  int frequency=1;
  char *dev = NULL;
  char *infi_path = NULL;
  char **application = NULL;
  ALGO_FUNC((*algorithm))=NULL;

  int _argc;
  argv = get_argv(&_argc);
  argc = _argc;
  
  algorithm = choose_frequency_neosched;
  
  if(argc==1)
    usage(argv);

  ////////////////////////////////
  char *outputname = "/dev/shm/neosched.data";
  output = fopen(outputname,"wb");
  
  atexit(flushexit);
  signal(15, flush);
  
  int c;
  while ((c = getopt (argc, argv, "ilhftdeoprsua")) != -1 && application==NULL)
    switch (c) {
    case 'f':
      frequency=atoi(argv[optind]);
      break;
    case 't':
      total_time=atoi(argv[optind]);
      delta=1;
      if(total_time==0) {
	total_time=1;
	delta=0;
      }
      break;
    case 'd':
      dev = argv[optind];
      break;
    case 'i':
      infi_path = argv[optind];
      break;
    case 'o':
      output = fopen(argv[optind],"wb");
      break;
    case 'e':
      application=&argv[optind];
      signal(17,sighandler);
      break;
    case 'p':
      perf_event_list(argv[optind], &nb_perf, &perf_indexes);
      perf_mode=0;
      break;
    case 'r':
      rapl_mode=0;
      break;
    case 'u':
      load_mode=0;
      break;
    case 's':
      stat_mode=0;
      break;
    case 'l':
      show_all_counters();
      exit(EXIT_SUCCESS);
    case 'a':
      switch (atoi(argv[optind])) {
      case 0:
	algorithm = choose_frequency_none;
	break;
      case 1:
	algorithm = choose_frequency_rapl;
	break;
      case 2:
	algorithm = choose_frequency_network;
	break;
      case 3:
	algorithm = choose_frequency_packet;
	break;
      case 4:
	algorithm = choose_frequency_all;
	break;
      case 5:
	algorithm = choose_frequency_nopct;
      }

      break;
    default:
      usage(argv);
    }
  
  //////////////////////////////////////
  //DVFS initialization
  init_dvfs();
  //////////////////////////////////////


  // Network initialization
  char ** network_sources = NULL;
  if(dev != NULL)
    network_sources = init_network(dev);
  long long network_values[4]={0,0,0,0};
  long long tmp_network_values[4]={0,0,0,0};
  get_network(network_values, network_sources);

  char ** infiniband_sources = NULL;
  if(infi_path != NULL)
    infiniband_sources = init_infiniband(infi_path);
  if(infiniband_sources == NULL)
    infi_path = NULL;
  long long infiniband_values[4]={0,0,0,0};
  long long tmp_infiniband_values[4]={0,0,0,0};
  get_network(infiniband_values, infiniband_sources);
  
  // Load initialization
  long long load_values[10]={0,0,0,0,0,0,0,0,0,0};
  long long tmp_load_values[10]={0,0,0,0,0,0,0,0,0,0};
  if(load_mode == 0)
    get_load(load_values);
  
  // RAPL initialization
  _rapl_t* rapl=NULL;
  size_t rapl_size=0;
  uint64_t * rapl_values=NULL;
  uint64_t * tmp_rapl_values=NULL;
  if(rapl_mode==0) {
    rapl = init_rapl(nbzones, rapl_zones);
    // prepare rapl data stores
    rapl_size = rapl->nb * sizeof(uint64_t);
    //rapl_values = malloc(rapl_size);
    rapl_values = calloc(sizeof(char), rapl_size);
    //tmp_rapl_values = malloc(rapl_size);
    tmp_rapl_values = calloc(sizeof(char), rapl_size);
    // initialize with dummy values
    get_rapl(rapl_values, rapl);
  }
  // Hardware Performance Counters initialization
  __u32* perf_type;
  __u64* perf_key;
  counter_t fd=0;
  long long *counter_values=NULL;
  if(perf_mode==0) {
    perf_type_key(&perf_type, &perf_key, perf_indexes, nb_perf);
    fd = init_counters(nb_perf, perf_type, perf_key);
    reset_counters(fd);
    // reading HPC will reset their values so no need for a buffer
    counter_values = malloc(nb_perf*sizeof(long long));
  }
  struct timespec ts;
  struct timespec ts_ref;

  /////////////////////////////////////////////////////
  /*
    fprintf(output, "#timestamp ");
    if(perf_mode==0)
    for(int i=0; i<nb_perf;i++)
    fprintf(output, "%s ", perf_static_info[perf_indexes[i]].name);
    if(dev!=NULL)
    fprintf(output, "rxp rxb txp txb ");
  if(infi_path!=NULL)
    fprintf(output, "irxp irxb itxp itxb ");

    if(rapl_mode==0)
    for (int r=0; r<rapl->nbpackages*rapl->nbzones; r++)
    fprintf(output, "%s%u ", rapl->names[r], (unsigned int)r/rapl->nbzones);

    if(load_mode==0)
    fprintf(output, "user nice system idle iowait irq softirq steal guest guest_nice ");
  
    if(stat_mode==0)
    fprintf(output, "overhead ");
    fprintf(output, "\n");
  */
  //////////////////////////////////////////////////////
  
  unsigned long int stat_data=0;
  if(perf_mode==0)
    start_counters(fd);

  for (int temps = 0; temps <total_time*frequency; temps+=delta) {
    clock_gettime(CLOCK_MONOTONIC, &ts_ref);

    // Get Data
    if(perf_mode==0)
      get_counters(fd, counter_values);
    if(dev != NULL)
      get_network(tmp_network_values, network_sources);
    if(infi_path != NULL)
      get_network(tmp_infiniband_values, infiniband_sources);

    if(rapl_mode==0)
      get_rapl(tmp_rapl_values, rapl); 
    if(load_mode==0)
      get_load(tmp_load_values);
    
    if(application != NULL) {

      if(fork()==0){
	execvp(application[0], application);
	exit(0);
      }
      pause();
      clock_gettime(CLOCK_MONOTONIC, &ts);
      if(ts.tv_nsec >= ts_ref.tv_nsec)
	fprintf(output, "%ld.%09ld ", (ts.tv_sec-ts_ref.tv_sec), ts.tv_nsec-ts_ref.tv_nsec);
      else
	fprintf(output, "%ld.%09ld ", (ts.tv_sec-ts_ref.tv_sec)-1,1000000000+ts.tv_nsec-ts_ref.tv_nsec);
    }
    else {
#ifdef DEBUG
      clock_gettime(CLOCK_MONOTONIC, &ts);
      fprintf(stderr, "%ld\n", (ts.tv_nsec-ts_ref.tv_nsec)/1000);
      //Indiv: mean: 148 std: 31 % med: 141 std: 28 %
      //Group: mean: 309 std: 41 % med: 297 std: 39 %
#endif
      if(stat_mode==0) {
	clock_gettime(CLOCK_MONOTONIC, &ts);
	if(ts.tv_nsec >= ts_ref.tv_nsec)
	  stat_data = ts.tv_nsec-ts_ref.tv_nsec;
	else
	  stat_data = 1000000000+ts.tv_nsec-ts_ref.tv_nsec;
      }
    
      // Treat Data
      ////////////////////////////////////
      /*
      fprintf(output, "%ld.%09ld ", ts_ref.tv_sec, ts_ref.tv_nsec);
      */
      ////////////////////////////////////
    }
    ///////////////////////////////////
    /*
    if(perf_mode==0)
      for(int i=0; i<nb_perf;i++) 
	fprintf(output, "%lld ", counter_values[i]);
    if(dev != NULL)
      for(int i=0; i<4; i++)
	fprintf(output, "%lld ", tmp_network_values[i]-network_values[i]);
    if(infi_path != NULL)
      for(int i=0; i<4; i++)
	fprintf(output, "%lld ", tmp_infiniband_values[i]-infiniband_values[i]);
    if(rapl_mode==0)
      for (int r=0; r<rapl->nbpackages*rapl->nbzones; r++)
	fprintf(output, "%ld ", tmp_rapl_values[r]-rapl_values[r]);
    if(load_mode==0)
      for(int i=0; i<10; i++)
	fprintf(output, "%lld ", tmp_load_values[i]-load_values[i]);
    
    if(stat_mode==0)
      fprintf(output, "%ld ", stat_data);
    
    fprintf(output, "\n");
    */
    ///////////////////////////////////
    //choose_frequency_rapl(tmp_rapl_values, rapl_values);
    algorithm(counter_values,
	      tmp_network_values, network_values,
	      tmp_infiniband_values, infiniband_values,
	      tmp_rapl_values, rapl_values,
	      tmp_load_values, load_values);

    if(application != NULL)
      break;
    if(rapl_mode==0)
      memcpy(rapl_values, tmp_rapl_values, rapl_size);
    if(load_mode==0)
      memcpy(load_values, tmp_load_values, sizeof(load_values));
    if(dev !=NULL)
      memcpy(network_values, tmp_network_values, sizeof(network_values));
    if(infi_path !=NULL)
      memcpy(infiniband_values, tmp_infiniband_values, sizeof(infiniband_values));
    clock_gettime(CLOCK_MONOTONIC, &ts);
    usleep(1000*1000/frequency-(ts.tv_nsec/1000)%(1000*1000/frequency));
  }

  if(rapl_mode==0){
    clean_rapl(rapl);
    free(rapl_values);
    free(tmp_rapl_values);
  }
  if(dev!=NULL)
    clean_network(network_sources);
  if(infi_path!=NULL)
    clean_network(infiniband_sources);
  if(perf_mode==0){
    clean_counters(fd);
    free(counter_values);
  }
}




