"""Profile the actual PCAP pipeline and write a cProfile report."""
from pathlib import Path
import cProfile, pstats, sys
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from benchmark_pcap import run
import asyncio
output = Path(__file__).parents[1] / "reports" / "final" / "pipeline_profile.pstats"
output.parent.mkdir(parents=True, exist_ok=True)
profiler = cProfile.Profile(); profiler.enable(); asyncio.run(run()); profiler.disable(); profiler.dump_stats(output)
text_path = output.with_suffix(".txt"); stats = pstats.Stats(profiler).sort_stats("cumulative"); stats.stream = open(text_path, "w", encoding="utf-8"); stats.print_stats(30); stats.stream.close(); print(f"Profile written to {output} and {text_path}")
