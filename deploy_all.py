import os
import shutil
import subprocess
import sys

def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    print(f"Scanning for demo workers in: {root_dir}")
    
    # Find all subdirectories containing pyproject.toml, wrangler.toml, and uv.lock
    demos = []
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            if (os.path.exists(os.path.join(item_path, "pyproject.toml")) and 
                os.path.exists(os.path.join(item_path, "wrangler.toml")) and
                os.path.exists(os.path.join(item_path, "uv.lock"))):
                demos.append(item)
                
    print(f"Found {len(demos)} demo workers: {', '.join(demos)}")
    
    for demo in demos:
        demo_path = os.path.join(root_dir, demo)
        print("\n" + "="*60)
        print(f"Processing demo: {demo}")
        print("="*60)
        
        # 1. Prepare python_modules directory
        py_modules_path = os.path.join(demo_path, "python_modules")
        if os.path.exists(py_modules_path):
            print(f"Cleaning existing python_modules directory...")
            shutil.rmtree(py_modules_path)
        os.makedirs(py_modules_path, exist_ok=True)
        
        # 2. Compile requirements.txt from pyproject.toml and uv.lock to get only production deps
        temp_req = os.path.join(demo_path, "temp_requirements.txt")
        print(f"Compiling production dependencies from uv.lock...")
        try:
            subprocess.run(
                ["uv", "pip", "compile", "pyproject.toml", "-o", "temp_requirements.txt"],
                cwd=demo_path,
                check=True,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error compiling dependencies for {demo}: {e}", file=sys.stderr)
            continue
            
        # 3. Install dependencies to python_modules
        print(f"Installing dependencies into python_modules...")
        try:
            # We use --no-compile to save space/time and avoid issues with pyodide runtime
            subprocess.run(
                ["uv", "pip", "install", "--target", "python_modules", "-r", "temp_requirements.txt", "--no-compile"],
                cwd=demo_path,
                check=True,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies for {demo}: {e}", file=sys.stderr)
            if os.path.exists(temp_req):
                os.remove(temp_req)
            continue
        finally:
            # Clean up temp file
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

if __name__ == "__main__":
    main()
