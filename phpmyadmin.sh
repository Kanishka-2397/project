#!/bin/bash
os_type() {
    os_type=$(uname -s)
    echo -e " WELCOME TO PHPMYADMIN AND MYSQL SCRIPT"  
    if [ "$1" = "centos" ]
        then
            echo -e " This is centos linux "
            sudo dnf update -y
            sudo dnf install mysql-server mysql -y
            sudo systemctl enable --now mysqld
            echo -e "MYSQL installation completed successfully"
            read -p "Enter username for Mysql= " mysql_uname
            read -sp "Enter password= " mysql_password
            sudo mysql -e "CREATE USER '$mysql_uname'@'localhost' IDENTIFIED BY '$mysql_password';"
            # Flush privileges
            sudo mysql -e "FLUSH PRIVILEGES;"
            echo -e "'$mysql_uname' created successfully."
            sudo dnf config-manager --set-enabled crb 
            sudo dnf install https://dl.fedoraproject.org/pub/epel/epel{,-next}-release-latest-9.noarch.rpm -y
            sudo dnf install phpmyadmin -y 
            echo -e "phpmyadmin is installation successfully"
            sudo dnf install http -y
            echo -e "http is installation successfully"
            systemctl enable --now httpd
            firewall-cmd --add-port=80/tcp --permanent 
            echo -e " Your system ip address is : \n"      
            ip a | grep 'inet ' | awk '{ print $2 }' | cut -d/ -f1 | tail -1

    elif [ "$1" = "del-centos" ]
        then
            echo -e "Removing MySQL..."
            sudo systemctl stop mysql
            sudo dnf remove mysql-server -y
            sudo dnf autoremove -y
            sudo dnf autoclean
            sudo rm -rf /etc/mysql /var/lib/mysql
            echo -e "MySQL removed."

            echo -e "Removing phpMyAdmin..."
            sudo dnf remove --purge phpmyadmin -y
            sudo dnf autoremove -y
            echo -e "phpMyAdmin removed."

            echo -e "Removing httpd.."
            sudo systemctl stop httpd
            sudo dnf autoremove -y
            echo -e "httpd removed."
        else 
            echo -e " This is not linux OS! Please check file!"
    fi

echo -e "The phpmysqladmin script executed successfully!"

}
os_type $1