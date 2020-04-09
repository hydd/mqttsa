import src.pdf_wrapper as pdfw

'''
This functions are used to dynamically create the report based
on the results of the attacks performed by MQTTSA.
'''

outdated_broker = "No"

# Authorization mechanism section
def authorization_report(pdfw, no_authentication, broker_info, auth_anyway, interface):
    pdfw.add_paragraph("Authentication")

    # No authentication mechanism detected -> write mitigations
    if no_authentication==True:
        pdfw.add_to_existing_paragraph("<b>[!] MQTTSA did not detect any authentication mechanism<b>")

        # Suggest X.509 certificates 
        pdfw.add_to_existing_paragraph('The tool was able to connect to the broker without specifying any kind of credential information. This may cause remote attackers to successfully connect to the broker. It is strongly advised to support authentication via X.509 client certificates.')
        
        if auth_anyway==True:
            pdfw.add_to_existing_paragraph('Moreover, it was able to intercept and use client credentials: please validate the broker configuration.')
        
        # Mitigations sections
        pdfw.add_sub_paragraph("Suggested mitigations")
        
        if broker_info != None:
            if "mosquitto" in broker_info:
                pdfw.add_to_existing_paragraph('Please follow those <a href="https://primalcortex.wordpress.com/2016/11/08/mqtt-mosquitto-broker-client-authentication-and-client-certificates/">guidelines</a> and modify Mosquitto\'s configuration according to the <a href="https://mosquitto.org/man/mosquitto-conf-5.html">official documentation</a>. An excerpt of a configuration file is provided below:<font size=6><p>     listener 8883<br/>     cafile /etc/mosquitto/certs/ca.crt<br/>     certfile /etc/mosquitto/certs/hostname.crt<br/>     keyfile /etc/mosquitto/certs/hostname.key<br/>     require_certificate true<br/>     use_identity_as_username true<br/>     crlfile /etc/mosquitto/certs/ca.crl</p></font>')
        else:
            pdfw.add_to_existing_paragraph('Refer here for additional informations:')
            pdfw.add_to_existing_paragraph('<a href="https://www.hivemq.com/blog/mqtt-security-fundamentals-x509-client-certificate-authentication">MQTT Security Fundamentals: X509 Client Certificate Authentication</a>')
            pdfw.add_to_existing_paragraph('<a href="https://thingsboard.io/docs/user-guide/certificates/">ThingsBoard: X.509 Certificate Based Authentication</a>')
    else:

        # Authentication mechanism detected
        pdfw.add_to_existing_paragraph("MQTTSA detected an authentication mechanism.")
        if auth_anyway==True:
            pdfw.add_to_existing_paragraph('<b>[!] However, it was able to intercept and use valid client credentials</b>.')
        elif interface != None:
            pdfw.add_to_existing_paragraph('Try to listen on a network interface to assess the possibility to sniff credentials. We suggest the use of Wireshark (https://www.wireshark.org/).')
            
# Information disclosure section
def information_disclosure_report(pdfw, topics_readable, sys_topics_readable, listening_time, broker_info, no_authentication):
    pdfw.add_paragraph("Information disclosure")
    
    # Description of the test performed by MQTTSA
    if no_authentication:
        pdfw.add_to_existing_paragraph("MQTTSA waited for "+str(listening_time)+" seconds after having subscribed to the '#' and '$SYS/#' topics. By default, clients who subscribe to the '#' topic can read to all the messages exchanged between devices and the ones subscribed to '$SYS/#' can read all the messages which includes statistics of the broker. Remote attackers could obtain specific information about the version of the broker to carry on more specific attacks or read messages exchanged by clients. <br>")

    # MQTTSA found readable topics -> suggest mitigations
    if len(topics_readable)+len(sys_topics_readable)>0:
        pdfw.add_to_existing_paragraph("<b>[!] MQTTSA successfully intercepted all the messages belonging to " +str(len(topics_readable)+len(sys_topics_readable)) + " topics, "+str(len(topics_readable))+" of them non $SYS. Intercepted data was stored in the 'messages' folder.</b>")
        if len(topics_readable)>0:
            pdfw.add_to_existing_paragraph("The non-SYS topics are: "+str(list(topics_readable)))
        if len(sys_topics_readable)>0:
            pdfw.add_to_existing_paragraph("The SYS topics are: "+str(list(sys_topics_readable)))

        # Mitigations    
        pdfw.add_sub_paragraph("Suggested mitigations")
        pdfw.add_to_existing_paragraph('It is strongly recommended to enforce an authorization mechanism in order to grant the access to confidential resources only to the specified users or devices. There are two possible approaches: Access Control List (ACL) and Role-based Access Control (RBAC).')
        
        if broker_info != None:
            if "mosquitto" in broker_info:
                pdfw.add_to_existing_paragraph('If restricting access via ACLs, please follow those <a href="http://www.steves-internet-guide.com/topic-restriction-mosquitto-configuration/">guidelines</a> and modify Mosquitto\'s configuration according to the <a href="https://mosquitto.org/man/mosquitto-conf-5.html">official documentation</a>. For instance, integrate the <i>acl_file</i> parameter (<i>acl_file /mosquitto/config/acls</i>) and restict a client to interact only on topics with his clientname as prefix (ACL <i>pattern readwrite topic/%c/#</i>)')
        else: 
            # additional information section
            pdfw.add_to_existing_paragraph('Additional information here:')
            pdfw.add_to_existing_paragraph('<a href="https://en.wikipedia.org/wiki/Access_control_list">Wikipedia: Access Control List</a>')
            pdfw.add_to_existing_paragraph('<a href="https://en.wikipedia.org/wiki/Role-based_access_control">Wikipedia: Role-based Access Control</a>')
            pdfw.add_to_existing_paragraph('<a href="https://www.hivemq.com/blog/mqtt-security-fundamentals-authorization/">MQTT Security Fundamentals: Authorization</a>')
            pdfw.add_to_existing_paragraph('<a href="https://www.hivemq.com/blog/mqtt-security-fundamentals-oauth-2-0-mqtt">MQTT Security Fundamentals: OAuth 2.0 & MQTT</a>')
            pdfw.add_to_existing_paragraph('<a href="http://www.steves-internet-guide.com/topic-restriction-mosquitto-configuration/">Configuring and Testing Mosquitto MQTT Topic Restrictions</a>')

        # MQTTSA did not found readable topics -> try to increase listening_time
    else:
        pdfw.add_to_existing_paragraph("MQTTSA was not able to intercept messages exchanged by clients.<br> It could be that no messages were exchanged durinfg this time interval, try to perform the assessment again, increasing the 'listening_time' parameter.")

# Tampering data section
def tampering_data_report(pdfw, topics_writable, sys_topics_writable, topics_readable, sys_topics_readable, text_message):
    pdfw.add_paragraph("Tampering data")

    # MQTTSA found readable topics -> check if there are writable topics
    if len(topics_readable)+len(sys_topics_readable)>0:
        pdfw.add_to_existing_paragraph("After having successfully intercepted some messages, MQTTSA automatically created a new message (having as a payload the string '"+str(text_message)+"') and attempted sending it to every topic it was able to intercept. Remote attackers could exploit it to write in specific topics pretending to be a client (by his ID); e.g., send tampered measures to a sensor. <br>")

        # MQTTSA found writable topics -> Suggestions (as in the information disclosure section)
        if len(sys_topics_writable)+len(topics_writable)>0:
            pdfw.add_to_existing_paragraph("<b>[!] MQTTSA was able to write in "+str(len(topics_writable)+len(sys_topics_writable))+" topics, with "+str(len(topics_writable))+" of them being non-$SYS.</b>") 
            pdfw.add_to_existing_paragraph("The topics were: "+str(list(topics_writable))+" "+str(list(sys_topics_writable)))
            pdfw.add_sub_paragraph("<br>Suggested mitigations")
            pdfw.add_to_existing_paragraph('The implementation of an authorization mechanism can mitigate this risk. Check the "Mitigations" paragraph in the section "Information disclosure".')

        # MQTTSA did not found writable topics
        else:
            pdfw.add_to_existing_paragraph("<b>MQTTSA was not able to write in any topic.</b>")

    # MQTTSA did not found readable topics -> try to repeat the assessment increasing the listening_time parameter
    else:
        pdfw.add_to_existing_paragraph("Since MQTTSA was not able to intercept any message, this vulnerability was not tested.<br>Try to perform the assessment again, increasing the 'listening_time' parameter.</b>")
    
# Broker fingerprinting section
def fingerprinting_report(pdfw, broker_info):
    global outdated_broker
    pdfw.add_paragraph("Broker Fingerprinting")
        
    brokers = {}
    with open("src/brokers_last_version.txt") as brokers_last_version:
        for line in brokers_last_version:
            name, version = line.partition("=")[::2]
            brokers[name.strip()] = version.strip()
        
    # Found informations regarding broker type and version -> check CVEs
    pdfw.add_to_existing_paragraph("MQTTSA detected the following MQTT broker: "+str(broker_info)+". ")
    if "mosquitto" in broker_info:
        if not brokers["mosquitto"] in broker_info:
            pdfw.add_to_existing_paragraph('<b>[!]Mosquitto version is not updated</b>: please refer to the last <a href="https://mosquitto.org/ChangeLog.txt">Change log</a> for bugs and security issues.')
            outdated_broker = "Yes"
        else:
            # The version detected is the last one
            pdfw.add_to_existing_paragraph('Mosquitto version is up-to-date.')
    elif "hivemq" in broker_info:
        if not brokers ["hivemq"] in broker_info:
            pdfw.add_to_existing_paragraph('<b>[!]HiveMQ version is not updated</b>: please refer to the last <a href="https://www.hivemq.com/changelog/">Change log</a> for bugs and security issues.')
            outdated_broker = "Yes"
        else:
            pdfw.add_to_existing_paragraph('HiveMQ version is up-to-date.')
    elif "vernemq" in broker_info:
        if not brokers ["vernemq"] in broker_info:
            pdfw.add_to_existing_paragraph('<b>[!]VerneMQ version is not updated</b>: please refer to the last <a href="https://github.com/vernemq/vernemq/blob/master/changelog.md">Change log</a> for bugs and security issues.')
            outdated_broker = "Yes"
        else:
            pdfw.add_to_existing_paragraph('VerneMQ version is up-to-date.')
    elif "emq" in broker_info:
        if not brokers ["emqx"] in broker_info:
            pdfw.add_to_existing_paragraph('<b>[!]EMQ version is not updated</b>: please refer to the last <a href="http://emqtt.io/changelogs">Change log</a> for bugs and security issues.')
            outdated_broker = "Yes"
        else:
            pdfw.add_to_existing_paragraph('EMQ version is up-to-date.')
    elif "adafruit" in broker_info:
        if not brokers ["adafruit"] in broker_info:
            pdfw.add_to_existing_paragraph('<b>[!]Adafruit IO version is not updated</b>: please refer to the last <a href="https://io.adafruit.com/blog/">Change log</a> for bugs and security issues.')
            outdated_broker = "Yes"
        else:
            pdfw.add_to_existing_paragraph('Adafruit IO is up-to-date.')
    elif "machine_head" in broker_info:
        if not brokers ["machine_head"] in broker_info:
            pdfw.add_to_existing_paragraph('<b>[!]Machine Head version is not updated</b>: please refer to the last <a href="https://github.com/clojurewerkz/machine_head/blob/master/ChangeLog.md">Change log</a> for bugs and security issues.')
            outdated_broker = "Yes"
        else:
            pdfw.add_to_existing_paragraph('Machine Head is up-to-date.')
    elif "moquette" in broker_info:
        if not brokers ["moquette"] in broker_info:
            pdfw.add_to_existing_paragraph('<b>[!]Moquette version is not updated</b>: please refer to the last <a href="https://github.com/andsel/moquette/blob/master/ChangeLog.txt">Change log</a> for bugs and security issues.')
            outdated_broker = "Yes"
        else:
            pdfw.add_to_existing_paragraph('Moquette is up-to-date.')
    elif "solace" in broker_info:
        if not brokers ["solace"] in broker_info:
            pdfw.add_to_existing_paragraph('<b>[!]Solace PubSub+ version is not updated</b>: please refer to the last <a href="https://products.solace.com/download/PUBSUB_STAND_RN">Release notes</a> for bugs and security issues.')
            outdated_broker = "Yes"
        else:
            pdfw.add_to_existing_paragraph('Solace PubSub+ is up-to-date.')
    elif "thingstream" in broker_info:
        if not brokers ["thingstream"] in broker_info:
            pdfw.add_to_existing_paragraph('<b>[!]Thingstream version is not updated</b>: please refer to the last <a href="https://sites.google.com/thingstream.io/docs/release-notes">Release notes</a> for bugs and security issues.')
            outdated_broker = "Yes"
        else:
            pdfw.add_to_existing_paragraph('Thingstream is up-to-date.')
    else:
        outdated_broker = "/"
        pdfw.add_to_existing_paragraph('MQTTSA was not able to detect if the broker is up-to-date. Please verify manually.')

# Sniffing data section
def sniffing_report(pdfw, usernames, passwords, clientids, listening_time, broker_info):
    pdfw.add_paragraph("Sniffing")

    # Description
    pdfw.add_to_existing_paragraph("MQTTSA used the specified interface to sniff the channel for "+str(listening_time)+" seconds and try to intercept credential information, such as <i>client-id, usernames</i> and <i>passwords</i>. <br> ")

    # MQTTSA found credential information -> mitigations
    if len(usernames)+len(passwords)+len(clientids)>0:
        pdfw.add_to_existing_paragraph("<b>[!] MQTTSA was able to intercept credential information.<b>") 
        pdfw.add_to_existing_paragraph(str(len(usernames))+" usernames obtained: "+', '.join(usernames)+ ".")
        pdfw.add_to_existing_paragraph(str(len(passwords))+" passwords obtained: "+', '.join(passwords)+ ".")
        pdfw.add_to_existing_paragraph(str(len(clientids))+" client-ids obtained: "+', '.join(clientids)+ ".")

        # Mitigations
        pdfw.add_sub_paragraph("<br>Suggested mitigations")
        pdfw.add_to_existing_paragraph('We strongly suggest to enforce TLS in MQTT (secure-MQTT). TLS provides a secure communication channel between clients and server: assuming the correct configuration of TLS (secure version and cipher suites), the content of the communication cannot be read or altered by third parties.')
           
        if broker_info != None:
            if "mosquitto" in broker_info:
                pdfw.add_to_existing_paragraph('In Mosquitto it is possible to set the <i>tls_version</i> parameter (e.g. to tlsv1.2). Refer to the <a href="https://mosquitto.org/man/mosquitto-conf-5.html">official documentation</a> for details')

        pdfw.add_to_existing_paragraph('<br>Warning: using MQTT over TLS could lead to a communication overhead and an increase in CPU usage, especially during the connection handshake. In devices with constrained resources, supporting TLS can have a severe impact. In these cases there are other (but less secure) solutions that could be used to secure the communication, such as encrypting only specific messages (for instance CONNECT and PUBLISH).')
        pdfw.add_to_existing_paragraph('<br>Additional information here:')
        pdfw.add_to_existing_paragraph('<a href="https://www.hivemq.com/blog/mqtt-security-fundamentals-tls-ssl">MQTT security fundamentals: TLS / SSL</a>')
        pdfw.add_to_existing_paragraph('<a href="https://www.hivemq.com/blog/how-does-tls-affect-mqtt-performance/">MQTT security fundamentals: how does TLS affect MQTT performance?</a>')
        pdfw.add_to_existing_paragraph('<a href="https://www.hivemq.com/blog/mqtt-security-fundamentals-payload-encryption">MQTT Security Fundamentals: MQTT Payload Encryption</a>')
        pdfw.add_to_existing_paragraph('<a href="https://www.hivemq.com/blog/mqtt-security-fundamentals-mqtt-message-data-integrity">MQTT Security Fundamentals: MQTT Message Data Integrity</a>')
        pdfw.add_to_existing_paragraph('<a href="https://dzone.com/articles/secure-communication-with-tls-and-the-mosquitto-broker">DZone: Secure Communication With TLS and the Mosquitto Broker</a>')

    # MQTTSA was unable to find credential information
    else:
        pdfw.add_to_existing_paragraph("MQTTSA was not able to intercept any credential information.") 

# Brute force section
def brute_force_report(pdfw, username, wordlist, password, no_pass):
    pdfw.add_paragraph("Brute force")

    # No password required to login
    if no_pass:
        pdfw.add_to_existing_paragraph("<b>[!] The brute force test was not needed. Authentication mechanism in use is enforced through only username.</b>")
    # Password required to login
    else:
        pdfw.add_to_existing_paragraph("<b>[!] The brute force test was succesfull.</b>")
        # No password found
        if password == None:
            pdfw.add_to_existing_paragraph("<b>[!] The brute force test was not able to determine a correct password to authenticate. Try to insert another wordlist.</b>")
            pdfw.add_to_existing_paragraph("Username provided: "+ str(username))
            pdfw.add_to_existing_paragraph("Wordlist path provided: "+ str(wordlist))
        
        # Password found
        else:
            pdfw.add_to_existing_paragraph("<b>[!] The brute force test was able to find a password to authenticate.</b>")
            pdfw.add_to_existing_paragraph("Username provided: "+ str(username))
            pdfw.add_to_existing_paragraph("Wordlist path provided: "+ str(wordlist))
            pdfw.add_to_existing_paragraph("Password found: "+ str(password))

        # Mitigations
        pdfw.add_sub_paragraph("<br>Suggested mitigations")
        pdfw.add_to_existing_paragraph('It is strongly recommended to implement a secure authentication mechanism. We suggest to implement authentication through X.509 certificates, however, a username/password enforcement can work as well, if a strong password is used.')
        pdfw.add_to_existing_paragraph('Additional information here:')
        pdfw.add_to_existing_paragraph('<br><a href="https://www.hivemq.com/blog/mqtt-security-fundamentals-authentication-username-password">MQTT Security Fundamentals: Authentication with Username and Password</a>')
        pdfw.add_to_existing_paragraph('<a href="https://en.wikipedia.org/wiki/Password_strength">Wikipedia: Password Strenght</a>')
        pdfw.add_to_existing_paragraph('<a href="https://www.hivemq.com/blog/mqtt-security-fundamentals-x509-client-certificate-authentication">MQTT Security Fundamentals: X509 Client Certificate Authentication</a>')
        pdfw.add_to_existing_paragraph('<a href="https://thingsboard.io/docs/user-guide/certificates/">ThingsBoard: X.509 Certificate Based Authentication</a>')

# Denial of Service section
def dos_report(pdfw, dos_connections, connection_difference, percentage_increment, broker_info):
    pdfw.add_paragraph("Denial of service")
    
    # Description
    if dos_connections != None:
        pdfw.add_to_existing_paragraph("MQTTSA tried to limit the availability of the service by saturating the number of clients connection and incrementing the processing time: it attempted connecting with "+str(dos_connections)+" clients, each publishing a 10MB message.") 
        
        pdfw.add_to_existing_paragraph("<b>[!]"+((str(connection_difference)+" clients were not able") if (connection_difference > 0) else ("All clients were able")) + " to connect; "+ str(percentage_increment) +"% is the overhead on publishing time caused by the heavy test messages.<b>")
            
        pdfw.add_to_existing_paragraph("<br>The tool is not currently able to determine if an existing client was disconnected : the user should check the logfile of the broker for any reconnection attempts or the clients. In case the test did not result in disconnections or delays, the test can be performed again increasing the <i>dos_connection</i> value.")
        
        # Mitigations 
        pdfw.add_sub_paragraph("<br>Suggested mitigations")
        pdfw.add_to_existing_paragraph('In case of MQTT environments with limited bandwidth capacity, it is recommended to prevent Denial of Service attacks by: implementing a firewall with appropriate rules, use a load balancer, limit the number of clients and packet dimension.')
        
        if broker_info != None:
            if "mosquitto" in broker_info:
                pdfw.add_to_existing_paragraph('In Mosquitto it is possible to set the <i>persistent_client_expiration</i>, <i>message_size_limit</i> and <i>max_connections</i> parameters in the configuration file (eg. to, respecively, 1h, 5120 and 5). Refer to the <a href="https://mosquitto.org/man/mosquitto-conf-5.html">official documentation</a> for details')
        
        pdfw.add_to_existing_paragraph('Additional information here:')
        pdfw.add_to_existing_paragraph('<a href="https://www.hivemq.com/blog/mqtt-security-fundamentals-securing-mqtt-systems">MQTT Security Fundamentals: Securing MQTT Systems</a>')
        pdfw.add_to_existing_paragraph('<a href="https://en.wikipedia.org/wiki/Password_strength">Mosquitto documentation: message_size_limit and max_connection</a>')
    else:
        pdfw.add_to_existing_paragraph("MQTTSA was not configured or able to perform a Denial of Service attack on the broker.")

# Malformed data section
def malformed_data_report(pdfw, mal_data, topic):
    pdfw.add_paragraph("Malformed data")
    # Description
    pdfw.add_to_existing_paragraph("MQTTSA tried to stress the broker by sending malformed packets in the "+str(topic)+" topic.")
    pdfw.add_to_existing_paragraph("An attacker could send malformed packets aiming at triggering errors to cause DoS or obtain information about the broker. We suggest to perform a full fuzzing test to stress the implementation with random well-crafted values. A fuzzer designed for MQTT is developed by F-Secure and can be found on the following link:")
    pdfw.add_to_existing_paragraph('<a href="https://github.com/F-Secure/mqtt_fuzz">Fuzzer F-Secure</a>')
    
    for malformed_data_object in mal_data:
        # print results
        pdfw.add_sub_paragraph("Parameter of the "+ malformed_data_object.packet +" packet tested: " + malformed_data_object.parameter)
        successful_values = "Values that did not generate an error: <br>"
        for val in malformed_data_object.successes:
            successful_values += str(val) + ", "
        successful_values = successful_values[:-2]
        pdfw.add_to_existing_paragraph(successful_values)
        error_values = "Values that generated an error and the related error: <br>"
        for val in malformed_data_object.errors:
            error_values += "Value: " + str(val.err_value) + ", Error: " + str(val.err_message) + "<br>"
        #ee = ee[:-2]
        pdfw.add_to_existing_paragraph("<br>"+error_values)

    pdfw.add_to_existing_paragraph("In case the report refer to values like '$' or '$topic', it might be possible to be affected from a bug included on an old version of Mosquitto. We strongly suggest to update the Mosquitto version to the last release to avoid having these issues.")
