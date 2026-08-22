--2023-06-06 01:08:58--  https://raw.githubusercontent.com/evilsocket/pwnagotchi/master/scripts/restore.sh
Herleiden van raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133, 185.199.109.133, 185.199.110.133, ...
Verbinding maken met raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... verbonden.
HTTP-verzoek is verzonden; wachten op antwoord... 200 OK
Lengte: 1235 (1,2K) [text/plain]
Wordt opgeslagen als: ‘restore.sh’

     0K .                                                     100%  117M=0s

2023-06-06 01:08:58 (117 MB/s) - '‘restore.sh’' opgeslagen [1235/1235]

it 1
	fi
	echo "@ Found backup file:"
	echo "\t${BACKUP}"
	echo -n "@ continue restroring this file? (y/n) "
	read CONTINUE
	CONTINUE=$(echo "${CONTINUE}" | tr "[:upper:]" "[:lower:]")
	if [ "${CONTINUE}" != "y" ]; then
		exit 1
	fi
fi
# username to use for ssh
UNIT_USERNAME=${UNIT_USERNAME:-pi}

ping -c 1 "${UNIT_HOSTNAME}" > /dev/null 2>&1 || {
  echo "@ unit ${UNIT_HOSTNAME} can't be reached, make sure it's connected and a static IP assigned to the USB interface."
  exit 1
}

echo "@ restoring $BACKUP to $UNIT_HOSTNAME ..."
cat ${BACKUP} | ssh "${UNIT_USERNAME}@${UNIT_HOSTNAME}" "sudo tar xzv -C /"
