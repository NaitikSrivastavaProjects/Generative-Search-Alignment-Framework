'''from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec


BASE_DIR = Path(__file__).resolve().parent


def load_plugins():
    # Load all plugin files

    plugins = []

    for file in BASE_DIR.glob("*.py"):

        # Skip main.py
        if file.name == Path(__file__).name:
            continue

        # Skip __init__.py
        if file.name.startswith("__"):
            continue

        try:

            spec = spec_from_file_location(
                file.stem,
                file
            )

            module = module_from_spec(spec)

            spec.loader.exec_module(module)

            # Find all checker functions
            for name in dir(module):

                if not name.startswith("check_"):
                    continue

                func = getattr(module, name)

                if callable(func):

                    plugins.append(
                        {
                            "file": file.name,
                            "function": name,
                            "callable": func
                        }
                    )

        except Exception as error:

            print(
                f"Failed to load plugin "
                f"{file.name}: {error}"
            )

    return plugins


def run_seo_analysis(context):
    # Execute all plugins

    report = {}

    print("\nStarting SEO Analysis...\n")

    plugins = load_plugins()

    if not plugins:

        print("No plugins found.")

        return report

    for plugin in plugins:

        function_name = plugin["function"]

        factor_name = (
            function_name
            .replace("check_", "")
            .replace("_", " ")
            .title()
        )

        print(
            f"Running {factor_name} "
            f"from {plugin['file']}"
        )

        try:

            result = plugin["callable"](context)

            report[
                result.get(
                    "factor",
                    factor_name
                )
            ] = result

        except Exception as error:

            report[factor_name] = {
                "factor": factor_name,
                "status": "Error",
                "error": str(error)
            }

    print("\nSEO Analysis Completed!")

    return report


def display_report(report):
    # Print final report

    print(
        "\n========== FINAL SEO REPORT ==========\n"
    )

    for factor, result in report.items():

        print(f"{factor}")

        print(result)

        print("-" * 50)


if __name__ == "__main__":

    # Website URL
    url = input(
        "Enter Website URL: "
    ).strip()

    # Primary keyword
    keyword = input(
        "Enter Primary Keyword (optional): "
    ).strip()

    # Multiple keywords
    keywords_input = input(
        "Enter Keywords separated by comma (optional): "
    ).strip()

    keywords = []

    if keywords_input:

        keywords = [
            item.strip()
            for item in keywords_input.split(",")
            if item.strip()
        ]

    # Competitor URL
    competitor_url = input(
        "Enter Competitor URL (optional): "
    ).strip()

    # Shared context for all plugins
    context = {
        "url": url,
        "keyword": keyword,
        "keywords": keywords,
        "competitor_url": competitor_url
    }

    report = run_seo_analysis(context)

    display_report(report)

'''
import importlib.util
from pathlib import Path
from utils.helpers import build_site_data


PLUGINS_DIR = Path(__file__).resolve().parent / "plugins"


def load_plugins():
    plugins = []

    # walk through every cluster folder inside plugins/
    for cluster in PLUGINS_DIR.iterdir():
        if not cluster.is_dir():
            continue

        # walk through every metric folder inside the cluster
        for metric_folder in cluster.iterdir():
            if not metric_folder.is_dir():
                continue

            # look for the main_metric_XX.py file inside the metric folder
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