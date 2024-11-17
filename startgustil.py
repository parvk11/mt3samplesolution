import subprocess

# Define the gsutil command
command = ['gsutil', '-q', '-m', 'cp', 'gs://magentadata/soundfonts/SGM-v2.01-Sal-Guit-Bass-V1.3.sf2', '.']

# Run the command
try:
    subprocess.run(command, check=True)
    print("File copied successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred: {e}")