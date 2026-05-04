# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  env_vars = {}
  env_file = File.expand_path(".env", __dir__)

  if File.exist?(env_file)
    File.readlines(env_file, chomp: true).each do |line|
      stripped = line.strip
      next if stripped.empty? || stripped.start_with?("#")

      key, value = stripped.split("=", 2)
      next if key.nil? || value.nil?

      env_vars[key.strip] = value.strip
    end
  end

  config.vm.box = "bento/ubuntu-22.04"
  config.vm.box_check_update = false
  config.vm.synced_folder ".", "/vagrant", SharedFoldersEnableSymlinksCreate: false

  config.vm.define "inventory-vm" do |inventory|
    inventory.vm.hostname = "inventory-vm"
    inventory.vm.network "private_network", ip: "192.168.56.11"
    inventory.vm.synced_folder "./srcs/inventory-app", "/home/vagrant/inventory-app"

    inventory.vm.provider "virtualbox" do |vb|
      vb.name = "inventory-vm"
      vb.gui = false
      vb.memory = "1024"
      vb.cpus = 1
    end

    inventory.vm.provision "shell", path: "scripts/inventory.sh", env: env_vars
  end

  config.vm.define "gateway-vm" do |gateway|
    gateway.vm.hostname = "gateway-vm"
    gateway.vm.network "private_network", ip: "192.168.56.12"
    gateway.vm.network "forwarded_port", guest: 8080, host: 8080, host_ip: "127.0.0.1", auto_correct: true
    gateway.vm.synced_folder "./srcs/api-gateway-app", "/home/vagrant/api-gateway-app"

    gateway.vm.provider "virtualbox" do |vb|
      vb.name = "gateway-vm"
      vb.gui = false
      vb.memory = "1024"
      vb.cpus = 1
    end

    gateway.vm.provision "shell", path: "scripts/gateway.sh", env: env_vars
  end

  config.vm.define "billing-vm" do |billing|
    billing.vm.hostname = "billing-vm"
    billing.vm.network "private_network", ip: "192.168.56.13"
    billing.vm.network "forwarded_port", guest: 15672, host: 15672, host_ip: "127.0.0.1", auto_correct: true
    billing.vm.synced_folder "./srcs/billing-app", "/home/vagrant/billing-app"

    billing.vm.provider "virtualbox" do |vb|
      vb.name = "billing-vm"
      vb.gui = false
      vb.memory = "1536"
      vb.cpus = 1
    end

    billing.vm.provision "shell", path: "scripts/billing.sh", env: env_vars
  end
end