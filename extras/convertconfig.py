import tomli_w as tomliw
import tomli
input_file_path = '/etc/pwnagotchi/config.toml'
output_file_path = 'config_saved.toml'
try:
    with open(input_file_path, 'rb') as input_file:
        config_data = tomli.load(input_file)
except FileNotFoundError:
    print(f"File not found: {input_file_path}")
    exit(1)
config_dict = dict(config_data)
with open(output_file_path, 'w') as output_file:
    output_file.write(tomliw.dumps(config_dict))
print(f"Config data saved to {output_file_path}")