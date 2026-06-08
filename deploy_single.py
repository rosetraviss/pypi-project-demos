import os
import shutil
import subprocess
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy_single.py <demo-directory-name>")
        sys.exit(1)
        
    demo = sys.argv[1]
    root_dir = os.path.abspath(os.path.dirname(__file__))
    demo_path = os.path.join(root_dir, demo)
    
    if not os.path.exists(demo_path) or not os.path.isdir(demo_path):
        print(f"Error: Directory '{demo}' not found under '{root_dir}'")
        sys.exit(1)
        
    if not (os.path.exists(os.path.join(demo_path, "pyproject.toml")) and 
            os.path.exists(os.path.join(demo_path, "wrangler.toml"))):
        print(f"Error: '{demo}' is not a valid demo worker directory (missing pyproject.toml or wrangler.toml)")
        sys.exit(1)
        
    print(f"Processing demo: {demo}")
    
    # 1. Prepare python_modules directory
    py_modules_path = os.path.join(demo_path, "python_modules")
    if os.path.exists(py_modules_path):
        print(f"Cleaning existing python_modules directory...")
        shutil.rmtree(py_modules_path)
    os.makedirs(py_modules_path, exist_ok=True)
    
    # 2. Compile requirements.txt
    temp_req = os.path.join(demo_path, "temp_requirements.txt")
    print(f"Compiling production dependencies...")
    try:
        subprocess.run(
            ["uv", "pip", "compile", "pyproject.toml", "-o", "temp_requirements.txt"],
            cwd=demo_path,
            check=True,
            shell=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error compiling dependencies for {demo}: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 2.5 Filter requirements to exclude heavy scientific/native stack packages not suitable/needed for Pyodide
    HEAVY_PACKAGES = {
        "numpy", "scipy", "pandas", "matplotlib", "numba", "llvmlite", "jax", "jaxlib", 
        "scikit-learn", "statsmodels", "scanpy", "anndata", "scvelo", "umap-learn", "zarr", 
        "igraph", "leidenalg", "python-igraph", "plotly", "shapely", "h5py", "numcodecs", 
        "contourpy", "pillow", "fonttools", "kiwisolver", "ml-dtypes", "opt-einsum", 
        "pygam", "pynndescent", "scfates", "palantir", "muon", "mudata", 
        "elpigraph-python", "adjusttext", "simpleppt", "mellon", "jaxopt", "atlas-smilies"
    }
    if os.path.exists(temp_req):
        with open(temp_req, "r") as f:
            lines = f.readlines()
        
        has_heavy = False
        filtered_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                filtered_lines.append(line)
                continue
            package_part = stripped.split("==")[0].split(">=")[0].split("<=")[0].split("!=")[0].split(" ")[0].lower().replace("_", "-")
            if any(package_part.startswith(p) or package_part == p for p in HEAVY_PACKAGES):
                print(f"Filtering out heavy/unsupported scientific package: {package_part}")
                has_heavy = True
            else:
                filtered_lines.append(line)
                
        if has_heavy:
            print(f"Warning: Demo '{demo}' depends on heavy/native libraries. Saving filtered dependencies list...")
            with open(temp_req, "w") as f:
                f.writelines(filtered_lines)

    # 3. Install dependencies to python_modules
    print(f"Installing dependencies into python_modules...")
    try:
        subprocess.run(
            ["uv", "pip", "install", "--target", "python_modules", "-r", "temp_requirements.txt", "--no-compile", "--no-deps"],
            cwd=demo_path,
            check=True,
            shell=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies for {demo}: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if os.path.exists(temp_req):
            os.remove(temp_req)
            
    # 4. Deploy using wrangler
    print(f"Deploying worker using wrangler...")
    try:
        subprocess.run(
            ["npx", "wrangler", "deploy"],
            cwd=demo_path,
            check=True,
            shell=True
        )
        print(f"Successfully deployed {demo}!")
    except subprocess.CalledProcessError as e:
        print(f"Error deploying {demo}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
