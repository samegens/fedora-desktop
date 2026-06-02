username = input('username')

# System tools

control "git is installed and working" do
  describe file('/usr/bin/git') do
    it { should exist }
    it { should be_executable }
  end
  describe command('git --version') do
    its('stdout') { should match /^git version/ }
    its('exit_status') { should eq 0 }
  end
end

control "docker is installed and working" do
  describe file('/usr/bin/docker') do
    it { should exist }
    it { should be_executable }
  end
  describe command('docker --version') do
    its('stdout') { should match /^Docker version/ }
    its('exit_status') { should eq 0 }
  end
end

control "terraform is installed and working" do
  describe file('/usr/local/bin/terraform') do
    it { should exist }
    it { should be_executable }
  end
  describe command('terraform --version') do
    its('stdout') { should match /^Terraform/ }
    its('exit_status') { should eq 0 }
  end
end

control "vagrant is installed and working" do
  describe file('/usr/bin/vagrant') do
    it { should exist }
    it { should be_executable }
  end
  describe command('vagrant --version') do
    its('stdout') { should match /^Vagrant/ }
    its('exit_status') { should eq 0 }
  end
end

control "cinc-auditor is installed and working" do
  describe file('/opt/cinc-auditor/bin/cinc-auditor') do
    it { should exist }
    it { should be_executable }
  end
  describe command('/opt/cinc-auditor/bin/cinc-auditor --version') do
    its('stdout') { should match /^[0-9]/ }
    its('exit_status') { should eq 0 }
  end
end

# CLI tools

control "starship is installed and working" do
  describe file('/usr/local/bin/starship') do
    it { should exist }
    it { should be_executable }
  end
  describe command('starship --version') do
    its('stdout') { should match /^starship/ }
    its('exit_status') { should eq 0 }
  end
end

control "fastfetch is installed and working" do
  describe file('/usr/bin/fastfetch') do
    it { should exist }
    it { should be_executable }
  end
  describe command('fastfetch --version') do
    its('stdout') { should match /^fastfetch/ }
    its('exit_status') { should eq 0 }
  end
end

control "azure cli is installed and working" do
  describe file('/usr/bin/az') do
    it { should exist }
    it { should be_executable }
  end
  describe command('az version') do
    its('stdout') { should match /azure-cli/ }
    its('exit_status') { should eq 0 }
  end
end

control "claude is installed and working" do
  describe file("/home/#{username}/.local/bin/claude") do
    it { should exist }
    it { should be_executable }
  end
  describe command('claude --version') do
    its('stdout') { should match /^[0-9]/ }
    its('exit_status') { should eq 0 }
  end
end

# Security scanning tools

control "gitleaks is installed and working" do
  describe file('/usr/local/bin/gitleaks') do
    it { should exist }
    it { should be_executable }
  end
  describe command('gitleaks version') do
    its('stdout') { should match /[0-9]/ }
    its('exit_status') { should eq 0 }
  end
end

control "trufflehog is installed and working" do
  describe file('/usr/local/bin/trufflehog') do
    it { should exist }
    it { should be_executable }
  end
  describe command('trufflehog --version') do
    its('exit_status') { should eq 0 }
  end
end

# Kubernetes tools

control "k3s is installed and working" do
  describe file('/usr/local/bin/k3s') do
    it { should exist }
    it { should be_executable }
  end
  describe command('k3s --version') do
    its('stdout') { should match /^k3s version/ }
    its('exit_status') { should eq 0 }
  end
end

control "k9s is installed and working" do
  describe file('/usr/local/bin/k9s') do
    it { should exist }
    it { should be_executable }
  end
  describe command('k9s version') do
    its('exit_status') { should eq 0 }
  end
end

control "helm is installed and working" do
  describe file('/usr/local/bin/helm') do
    it { should exist }
    it { should be_executable }
  end
  describe command('helm version') do
    its('stdout') { should match /Version:/ }
    its('exit_status') { should eq 0 }
  end
end

# Development tools

control "vscode is installed and working" do
  describe file('/usr/bin/code') do
    it { should exist }
    it { should be_executable }
  end
  describe command('code --version') do
    its('stdout') { should match /^[0-9]/ }
    its('exit_status') { should eq 0 }
  end
end

control "go is installed and working" do
  describe file('/usr/local/go/bin/go') do
    it { should exist }
    it { should be_executable }
  end
  describe command('/usr/local/go/bin/go version') do
    its('stdout') { should match /^go version/ }
    its('exit_status') { should eq 0 }
  end
end

control "rustc is installed and working" do
  describe file("/home/#{username}/.cargo/bin/rustc") do
    it { should exist }
    it { should be_executable }
  end
  describe command("/home/#{username}/.cargo/bin/rustc --version") do
    its('stdout') { should match /^rustc/ }
    its('exit_status') { should eq 0 }
  end
end

control "cargo is installed and working" do
  describe file("/home/#{username}/.cargo/bin/cargo") do
    it { should exist }
    it { should be_executable }
  end
  describe command("/home/#{username}/.cargo/bin/cargo --version") do
    its('stdout') { should match /^cargo/ }
    its('exit_status') { should eq 0 }
  end
end

control "p4merge is installed and working" do
  describe file('/usr/local/bin/p4merge') do
    it { should exist }
    it { should be_executable }
  end
end

control "Node.js version is >= 20" do
  describe command('node --version') do
    its('exit_status') { should eq 0 }
    its('stdout') { should match /^v(2[0-9]|[3-9][0-9]|\d{3,})/ }
  end
end

control "npm version is >= 10" do
  describe command('npm --version') do
    its('exit_status') { should eq 0 }
    its('stdout') { should match /^([1-9][0-9]|\d{3,})/ }
  end
end
