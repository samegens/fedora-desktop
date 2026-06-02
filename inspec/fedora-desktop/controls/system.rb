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

control "ssh config is in place with correct permissions" do
  describe file("/home/#{username}/.ssh/config") do
    it { should exist }
    its('mode') { should cmp '0600' }
    its('owner') { should eq username }
    its('content') { should match /github\.com/ }
    its('content') { should match /liteserver/ }
  end
end

for key_name in ['cubi', 'fitlet', 'liteserver', 'github_samegens', 'github_blauwe-lucht', 'gitlab'] do
  control "SSH key #{key_name} is installed with correct permissions" do
    this_key = key_name
    describe file("/home/#{username}/.ssh/#{this_key}") do
      it { should exist }
      its('mode') { should cmp '0600' }
      its('owner') { should eq username }
    end
  end
end

control "homeserver SSH key symlink is in place" do
  describe file("/home/#{username}/.ssh/homeserver") do
    it { should exist }
    it { should be_symlink }
  end
end
