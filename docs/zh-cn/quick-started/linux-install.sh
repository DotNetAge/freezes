#!/bin/bash 

echo "-------------------Checking packages-----------------------"

sudo apt-get update
sudo apt-get install python-dev python-pip python-virtualenv node-less coffeescript

echo "---------------------------------Freezes installer---------------------------------"
echo "Please enter the new website name"

read user_path

if [ ! -d "$user_path" ]; 
	then
		sudo mkdir $user_path 
	else
		echo "The website name is exists still create the website to this folder ?"
		echo " 'y' to continue 'n' to exit [y/n]?"
		read is_continue
		if [ $is_continue = "n" ]; then 
			return
		fi
fi

cd $user_path

if [ ! -d "venv" ]; 
	then
		echo "---------------------------------Preparing the virtualenv---------------------------------"
		sudo virtualenv venv
		source venv/bin/activate

		echo "---------------------------------Installing freezes please wait.. ---------------------------------"
		sudo pip install freezes 

		sudo freezes new
	else
		source venv/bin/activate
		echo "--------------------------------- Upgrading Freezes to latest version ----------------------------------"
		sudo pip install freezes --upgrade
fi


sudo freezes