import yaml

with open('environment.yml') as f:
    env = yaml.safe_load(f)

dependencies = env['dependencies']
pip_dependencies = []

for dep in dependencies:
    if isinstance(dep, dict) and 'pip' in dep:
        pip_dependencies.extend(dep['pip'])
    else:
        pip_dependencies.append(dep)

with open('pyproject.toml', 'w') as f:
    f.write('[build-system]\n')
    f.write('requires = ["setuptools", "wheel"]\n')
    f.write('build-backend = "setuptools.build_meta"\n\n')
    f.write('[project]\n')
    f.write('name = "your_project_name"\n')
    f.write('version = "0.1.0"\n')
    f.write('description = "A brief description of your project"\n')
    f.write('authors = [{ name = "Your Name", email = "your.email@example.com" }]\n')
    f.write('dependencies = [\n')
    for dep in pip_dependencies:
        f.write(f'    "{dep}",\n')
    f.write(']\n')