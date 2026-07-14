import importlib.util
from pathlib import Path
from utils.helpers import build_site_data
from utils.ai_batch import run_ai_batch


PLUGINS_DIR = Path(__file__).resolve().parent / "plugins"


def load_plugins():
    plugins = []
    loaded_names = set()

    for cluster in sorted(PLUGINS_DIR.iterdir()):
        if not cluster.is_dir():
            continue

        for metric_folder in sorted(cluster.iterdir()):
            if not metric_folder.is_dir():
                continue

            for file in metric_folder.glob("main_metric_*.py"):
                if file.name in loaded_names:
                    print(f"Duplicate skipped: {file}")
                    continue

                loaded_names.add(file.name)
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)

                try:
                    spec.loader.exec_module(module)
                    if hasattr(module, "run"):
                        module._cluster = cluster.name
                        module._factor = file.stem
                        plugins.append(module)
                    else:
                        # file loaded but no run() function
                        error_msg = f"No run() function found in {file.name}"
                        print(error_msg)
                        plugins.append(type('FailedPlugin', (), {
                            '_cluster': cluster.name,
                            '_factor': file.stem,
                            'run': lambda self, sd, msg=error_msg, stem=file.stem, cname=cluster.name: {
                                "factor": stem,
                                "score": None,
                                "status": "Error",
                                "details": {"error": msg},
                                "recommendations": [],
                                "error": msg,
                                "_cluster": cname
                            }
                        })())

                except Exception as e:
                    error_msg = str(e)
                    print(f"Failed to load {file.name}: {error_msg}")
                    # still register so cluster appears as a tab
                    plugins.append(type('FailedPlugin', (), {
                        '_cluster': cluster.name,
                        '_factor': file.stem,
                        'run': lambda self, sd, msg=error_msg, stem=file.stem, cname=cluster.name: {
                            "factor": stem,
                            "score": None,
                            "status": "Error",
                            "details": {"error": msg},
                            "recommendations": [],
                            "error": msg,
                            "_cluster": cname
                        }
                    })())

    return plugins


def run_analysis(url, keyword="", keywords=None, competitor_url=""):
    site_data = build_site_data(url, keyword, keywords, competitor_url)
    site_data.ai_results = run_ai_batch(site_data)

    plugins = load_plugins()
    results = []

    for plugin in plugins:
        try:
            result = plugin.run(site_data)
            result["_cluster"] = getattr(plugin, "_cluster", "other")
            results.append(result)
        except Exception as e:
            results.append({
                "factor": getattr(plugin, "_factor", "Unknown"),
                "score": None,
                "status": "Error",
                "details": {"error": str(e)},
                "recommendations": [],
                "error": str(e),
                "_cluster": getattr(plugin, "_cluster", "other")
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
        print(f"  Cluster: {result['_cluster']}")
    print("\n" + "=" * 60)