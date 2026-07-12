import importlib.util
from pathlib import Path
from utils.helpers import build_site_data
from utils.ai_batch import run_ai_batch


PLUGINS_DIR = Path(__file__).resolve().parent / "plugins"


def load_plugins():
    plugins = []

    for cluster in PLUGINS_DIR.iterdir():
        if not cluster.is_dir():
            continue

        for metric_folder in cluster.iterdir():
            if not metric_folder.is_dir():
                continue

            for file in metric_folder.glob("main_metric_*.py"):
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    if hasattr(module, "run"):
                        plugins.append(module)
                except Exception as e:
                    print(f"Failed to load {file.name}: {e}")

    return plugins


def run_analysis(url, keyword="", keywords=None, competitor_url=""):
    site_data = build_site_data(url, keyword, keywords, competitor_url)

    # run AI batch once before all plugins so ai_results are ready
    site_data.ai_results = run_ai_batch(site_data)

    plugins = load_plugins()
    results = []

    for plugin in plugins:
        try:
            result = plugin.run(site_data)
            results.append(result)
        except Exception as e:
            results.append({
                "factor": getattr(plugin, "__name__", "Unknown"),
                "score": None,
                "status": "Error",
                "details": {},
                "recommendations": [],
                "error": str(e)
            })

    return results


if __name__ == "__main__":
    url = input("Enter URL to analyze: ").strip()
    keyword = input("Enter keyword (optional): ").strip()
    results = run_analysis(url, keyword)

    print("\n" + "=" * 60)
    for result in results:
        print(f"\n{result['factor']}")
        print(f"  Score  : {result['score']}")
        print(f"  Status : {result['status']}")
        if result.get("recommendations"):
            for rec in result["recommendations"]:
                print(f"  → {rec}")
    print("\n" + "=" * 60)