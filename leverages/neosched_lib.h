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

void set_pct(int value);
void init_dvfs();
void set_freq(int value);

#define ALGO_FUNC(name) void name(long long * counters, long long *new_network, long long *old_network, long long* new_infiniband, long long *old_infiniband, uint64_t *new_rapl, uint64_t *old_rapl, long long *new_load, long long *old_load)

ALGO_FUNC(choose_frequency_rapl);
ALGO_FUNC(choose_frequency_network);
ALGO_FUNC(choose_frequency_packet);
ALGO_FUNC(choose_frequency_all);
ALGO_FUNC(choose_frequency_none);
ALGO_FUNC(choose_frequency_nopct);

ALGO_FUNC(choose_frequency_neosched);
char **get_argv(int *argc);
