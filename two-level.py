import m5
from m5.objects import *
from new_cache import *
from optparse import OptionParser
parser = OptionParser() 
parser.add_option('--o3', action="store_true") 
parser.add_option('--inorder', action="store_true") 
parser.add_option('--cpu_clock', type="string", default="2GHz") 
parser.add_option('--ddr3_1600', action="store_true") 
parser.add_option('--ddr3_2133', action="store_true") 
parser.add_option('--ddr4_2400', action="store_true") 
parser.add_option('--lpddr2_1066', action="store_true")
parser.add_option('--wideio_200', action="store_true") 
parser.add_option('--lpddr3_1600', action="store_true") 
parser.add_option('--gddr5_4000', action="store_true")
parser.add_option('--l1i_size', type="string", default="32kB")
parser.add_option('--l1i_assoc', type="int", default=8)
parser.add_option('--l1d_size', type="string", default="32kB")
parser.add_option('--l1d_assoc', type="int", default=8)
parser.add_option('--l2_size', type="string", default="1MB") 
parser.add_option('--l2_assoc', type="int", default=16)
parser.add_option('--lru', action="store_true")
parser.add_option('--rrlip', action="store_true")
parser.add_option('--mixed', action="store_true")
parser.add_option('--wl1', action="store_true")
parser.add_option('--wl2', action="store_true")
parser.add_option('--wl3', action="store_true")
parser.add_option('--wl4', action="store_true")
(options, args) = parser.parse_args()


root = Root()
root.full_system = False
root.system = System()
#root = Root( full_system = False, system = System() )
root.system.clk_domain = SrcClockDomain()
root.system.clk_domain.clock = '2GHz'
root.system.clk_domain.voltage_domain = VoltageDomain()
root.system.mem_mode = 'timing'
root.system.mem_ranges = [AddrRange ('2048MB')]
#root.system.mem_ctrl = DDR3_1600_8x8()
############### modify memory controller ########################### 
if options.ddr3_1600:
	root.system.mem_ctrl = DDR3_1600_8x8() 
elif options.ddr3_2133:
	root.system.mem_ctrl = DDR3_2133_8x8() 
elif options.ddr4_2400:
	root.system.mem_ctrl = DDR4_2400_16x4() 
elif options.lpddr2_1066:
	root.system.mem_ctrl = LPDDR2_S4_1066_1x32() 
elif options.wideio_200:
	root.system.mem_ctrl = WideIO_200_1x128() 
elif options.lpddr3_1600:
	root.system.mem_ctrl = LPDDR3_1600_1x32() 
elif options.gddr5_4000:
	root.system.mem_ctrl = GDDR5_4000_2x32()
else:
	root.system.mem_ctrl = DDR3_1600_8x8() #default setting 
############### modify memory controller ###########################
root.system.mem_ctrl.range = root.system.mem_ranges[0]
#root.system.cpu = TimingSimpleCPU()
############### modify cpu type ########################### 
if options.o3:
	root.system.cpu = DerivO3CPU() 
elif options.inorder:
	root.system.cpu = MinorCPU() 
else:
	root.system.cpu = TimingSimpleCPU() 
############### modify cpu type ###########################
############### modify cpu clock domain ########################### 
root.system.cpu_clk_domain = SrcClockDomain()
root.system.cpu_clk_domain.clock = options.cpu_clock
root.system.cpu_clk_domain.voltage_domain = VoltageDomain()
root.system.cpu.clk_domain = root.system.cpu_clk_domain
############### modify clock domain ##############################
root.system.cpu.max_insts_any_thread = 100000000 #set maximum instructions as 10000000


root.system.cpu.icache = L1ICache()
root.system.cpu.dcache = L1DCache()
root.system.l2cache = L2Cache()
root.system.cpu.icache.size = options.l1i_size 
root.system.cpu.dcache.size = options.l1d_size 
root.system.l2cache.size = options.l2_size
root.system.cpu.icache.assoc = options.l1i_assoc 
root.system.cpu.dcache.assoc = options.l1d_assoc 
root.system.l2cache.assoc = options.l2_assoc
#root.system.l2cache.threshold = options.l2_threshold

root.system.membus = SystemXBar()
#root.system.cpu.icache_port = root.system.membus.slave
#root.system.cpu.dcache_port = root.system.membus.slave
root.system.cpu.icache.cpu_side = root.system.cpu.icache_port
root.system.cpu.dcache.cpu_side = root.system.cpu.dcache_port
root.system.l2bus = L2XBar()
root.system.cpu.icache.mem_side = root.system.l2bus.slave
root.system.cpu.dcache.mem_side = root.system.l2bus.slave
root.system.l2cache.cpu_side = root.system.l2bus.master
root.system.l2cache.mem_side = root.system.membus.slave

root.system.mem_ctrl.port = root.system.membus.master
root.system.cpu.createInterruptController()
root.system.system_port = root.system.membus.slave
if options.rrlip:
	root.system.cpu.icache.replacement_policy = RRLIPRP()
	root.system.cpu.dcache.replacement_policy = RRLIPRP()
	root.system.l2cache.replacement_policy = RRLIPRP()
elif options.lru:
	root.system.cpu.icache.replacement_policy = LRURP()
	root.system.cpu.dcache.replacement_policy = LRURP()
	root.system.l2cache.replacement_policy = LRURP()
elif options.mixed:
	root.system.cpu.icache.replacement_policy = LRURP()
	root.system.cpu.dcache.replacement_policy = LRURP()
	root.system.l2cache.replacement_policy = RRLIPRP()
else:
	root.system.cpu.icache.replacement_policy = LRURP()
	root.system.cpu.dcache.replacement_policy = LRURP()
	root.system.l2cache.replacement_policy = LRURP()

# root.system.cpu.interrupt[0].pio = root.system.membus.master
# root.system.cpu.interrupt[0].int_master = root.system.membus.slave
# root.system.cpu.interrupt[0].int_slave = root.system.membus.master
process = Process()
#process.cmd = ['tests/test-progs/hello/bin/arm/linux/hello']
if options.wl1:
	process.cmd = ['test_bench/2MM/2mm_base']
elif options.wl2:
	process.cmd = ['test_bench/BFS/bfs','-f','test_bench/BFS/USA-road-d.NY.gr'] 
elif options.wl3:
	process.cmd = ['test_bench/bzip2/bzip2_base.amd64-m64-gcc42-nn','test_bench/bzip2/input.source','280']
elif options.wl4:
	process.cmd = ['test_bench/mcf/mcf_base.amd64-m64-gcc42-nn','test_bench/mcf/inp.in']
else:
	process.cmd = ['tests/test-progs/hello/bin/arm/linux/hello']
root.system.cpu.workload = process
root.system.cpu.createThreads()
m5.instantiate()
exit_event = m5.simulate()
print('Existing @ tick', 'because', exit_event.getCause())
