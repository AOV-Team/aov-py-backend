# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Every Vagrant development environment requires a box.
  config.vm.box = "ubuntu/trusty64"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine.
  config.vm.network "forwarded_port", guest: 8000, host: 8000

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.33.10"

  # Share an additional folder to the guest VM
  config.vm.synced_folder ".", "/vagrant", id: "vagrant-root", :mount_options => ["dmode=777","fmode=777"]

  # Install Python essentials
  config.vm.provision :shell, path: "scripts/vagrant.sh"
end