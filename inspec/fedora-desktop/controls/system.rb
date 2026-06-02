username = input('username')

# Services

['docker', 'sshd', 'k3s'].each do |svc|
  control "#{svc} service is enabled and running" do
    describe service(svc) do
      it { should be_enabled }
      it { should be_running }
    end
  end
end

# Group memberships

['docker', 'video', 'dialout', 'adm'].each do |grp|
  control "user is in #{grp} group" do
    describe user(username) do
      its('groups') { should include grp }
    end
  end
end

# NFS mounts

control "homeserver-public NFS share is mounted and accessible" do
  describe mount('/mnt/homeserver-public') do
    it { should be_mounted }
    its('device') { should eq 'cubi:/data/public' }
    its('type') { should eq 'nfs4' }
  end
  describe directory('/mnt/homeserver-public') do
    it { should be_readable }
  end
end

# Kernel parameters

control "vm.max_map_count is set to 262144 for OpenSearch" do
  describe kernel_parameter('vm.max_map_count') do
    its('value') { should eq 262144 }
  end
end

# Hosts file

control "hosts file contains required entries" do
  describe file('/etc/hosts') do
    its('content') { should match /5\.2\.74\.226\s+liteserver/ }
    its('content') { should match /liteserver-tst/ }
    its('content') { should match /fitlet-tst/ }
    its('content') { should match /youtube\.com/ }
  end
end

# Locale

control "locale is set to en_US.UTF-8" do
  describe file('/etc/default/locale') do
    it { should exist }
    its('content') { should match /LANG=en_US\.UTF-8/ }
  end
end

# Config files

control ".inputrc is configured" do
  describe file("/home/#{username}/.inputrc") do
    it { should exist }
    its('owner') { should eq username }
    its('content') { should match /completion-ignore-case On/ }
  end
end

control "go PATH script is in place" do
  describe file('/etc/profile.d/go.sh') do
    it { should exist }
    its('content') { should match %r{/usr/local/go/bin} }
  end
end

control "ansible log directory exists with correct ownership" do
  describe directory('/var/log/ansible') do
    it { should exist }
    its('owner') { should eq username }
  end
end

# SSH

control "ssh directory has correct permissions" do
  describe file("/home/#{username}/.ssh") do
    it { should be_directory }
    its('mode') { should cmp '0700' }
    its('owner') { should eq username }
  end
end

control "ssh config is in place with correct permissions" do
  describe file("/home/#{username}/.ssh/config") do
    it { should exist }
    its('mode') { should cmp '0600' }
    its('owner') { should eq username }
    its('content') { should match /github\.com/ }
    its('content') { should match /liteserver/ }
  end
end

ssh_keys = ['cubi', 'fitpc', 'fitlet', 'fitlet-tst', 'fitlet-acc', 'liteserver',
            'liteserver-tst', 'github_samegens', 'github_blauwe-lucht', 'gitlab',
            'github_adopteerregenwoud']

ssh_keys.each do |key_name|
  control "SSH private key #{key_name} is installed with correct permissions" do
    describe file("/home/#{username}/.ssh/#{key_name}") do
      it { should exist }
      its('mode') { should cmp '0600' }
      its('owner') { should eq username }
    end
  end

  control "SSH public key #{key_name}.pub is installed" do
    describe file("/home/#{username}/.ssh/#{key_name}.pub") do
      it { should exist }
      its('owner') { should eq username }
    end
  end
end

control "homeserver SSH private key symlink is in place" do
  describe file("/home/#{username}/.ssh/homeserver") do
    it { should exist }
    it { should be_symlink }
  end
end

control "homeserver SSH public key symlink is in place" do
  describe file("/home/#{username}/.ssh/homeserver.pub") do
    it { should exist }
    it { should be_symlink }
  end
end

# Git config

control "git is configured correctly" do
  describe file("/home/#{username}/.gitconfig") do
    it { should exist }
    its('content') { should match /name\s*=\s*Sebastiaan/ }
    its('content') { should match /email\s*=\s*\S+/ }
    its('content') { should match /fileMode\s*=\s*true/i }
    its('content') { should match /autoSetupRemote\s*=\s*true/i }
    its('content') { should match /defaultBranch\s*=\s*main/ }
    its('content') { should match /default\s*=\s*current/ }
  end
end

# Bashrc

control ".bashrc is configured" do
  describe file("/home/#{username}/.bashrc") do
    it { should exist }
    its('content') { should match /\.cargo\/bin/ }
    its('content') { should match /KUBECONFIG=\/etc\/rancher\/k3s\/k3s\.yaml/ }
    its('content') { should match /alias ll=/ }
    its('content') { should match /alias k='kubectl'/ }
  end
end

# Python virtual environments

['ansible-latest', 'blauwe-lucht-rpa', 'ansible-homedisplay'].each do |venv|
  control "Python venv #{venv} exists" do
    describe file("/home/#{username}/python3-venv/#{venv}/bin/activate") do
      it { should exist }
      its('owner') { should eq username }
    end
  end
end
