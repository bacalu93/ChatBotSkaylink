resource "null_resource" "pip_install" {
  triggers = {
    always_run = "${timestamp()}"
  }
  provisioner "local-exec" {
    command = <<-EOT
      # List the contents of the layer directory to check for requirements.txt
      echo "Checking layer directory"
      ls -la ${var.source_dir}/layer/
      
      # Create a virtual environment and ensure pip is installed
      echo "Creating virtual environment"
      python3 -m venv venv
      ./venv/bin/python -m ensurepip --upgrade
      ./venv/bin/python -m pip install --upgrade pip setuptools wheel
      ./venv/bin/python -m pip install pytest==7.0.1

      # Check Python and pip versions
      ./venv/bin/python --version
      ./venv/bin/python -m pip --version
      ./venv/bin/python -m pip list
      
      # Create requirements.txt
      echo "Creating requirements.txt"
      cat <<EOF > ${var.source_dir}/layer/requirements.txt
      python-jose==3.3.0
      requests==2.32.3
      boto3==1.34.137
      markdown==3.6
      langdetect==1.0.9
      EOF

      # Activate virtual environment
      echo "Activating virtual environment"
      source ./venv/bin/activate
      
      # Install application dependencies using the virtual environment's Python
      if [ -s ${var.source_dir}/layer/requirements.txt ]; then
        echo "Installing requirements"
        ./venv/bin/python -m pip install -r ${var.source_dir}/layer/requirements.txt --no-cache-dir -t ${var.source_dir}/layer/python/lib/python3.12/site-packages
      else
        echo "requirements.txt not found!"
      fi
      
      # Verify installation of dependencies
      ./venv/bin/python -m pip list | grep -E 'jose|requests'
      
      # Install pytest and boto3
      ./venv/bin/python -m pip install pytest boto3

      # Run tests if the tests folder exists
      if [ -d "${var.source_dir}/tests" ]; then
        echo "Running tests"
        ./venv/bin/python -m pytest ${var.source_dir}/tests
      else
        echo "Tests folder does not exist, skipping tests."
      fi
    EOT
  }
}
