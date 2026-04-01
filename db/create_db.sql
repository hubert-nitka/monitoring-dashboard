CREATE TYPE status AS ENUM ('online', 'offline', 'unreachable', 'maintenance', 'decommissioned');
CREATE TYPE priority AS ENUM ('critical', 'high', 'medium', 'low');

CREATE  TABLE devices  (
	id SERIAL PRIMARY KEY,
	hostname VARCHAR(255) NOT NULL,
	IP_address INET NOT NULL,
	serial_number VARCHAR(255) NOT NULL,
	type_id INTEGER,
	vendor_id INTEGER,
	model VARCHAR(255),
	priority PRIORITY NOT NULL,
	software_version VARCHAR(255),
	status STATUS NOT NULL,
	last_seen TIMESTAMP NOT NULL
);

CREATE TABLE vlans (
	vlan_id INTEGER PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	network_cidr CIDR NOT NULL,
	dhcp_enabled BOOLEAN NOT NULL
);

CREATE TABLE device_vlans (
	device_id INTEGER NOT NULL,
	vlan_id INTEGER NOT NULL,
	PRIMARY KEY (device_id, vlan_id)
);

CREATE TABLE device_snapshots (
	id SERIAL PRIMARY KEY,
	device_id INTEGER NOT NULL,
	timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	software_version VARCHAR(255),
	status STATUS NOT NULL
);

CREATE TABLE interfaces (
	id SERIAL PRIMARY KEY,
	device_id INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL,
	ip_address INET,
	description VARCHAR(255),
	admin_status VARCHAR(50) NOT NULL,
	oper_status VARCHAR(50) NOT NULL,
	in_pkt BIGINT,
	out_pkt BIGINT,
	in_errors INTEGER,
	out_errors INTEGER,
	out_drops INTEGER,
	last_updated TIMESTAMP NOT NULL
);

CREATE TABLE interface_history (
	id SERIAL PRIMARY KEY,
	interface_id INTEGER NOT NULL,
	timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	old_status VARCHAR(50),
	new_status VARCHAR(50) NOT NULL
);

CREATE TABLE device_types (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL
);

CREATE TABLE vendors (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL
);

ALTER TABLE interfaces 
ADD CONSTRAINT fk_devices
	FOREIGN KEY (device_id)
	REFERENCES devices(id)
	ON DELETE CASCADE,
ADD CONSTRAINT uc_interface
	UNIQUE (device_id, name);

ALTER TABLE interface_history
ADD CONSTRAINT fk_interfaces
	FOREIGN KEY (interface_id)
	REFERENCES interfaces(id)
	ON DELETE CASCADE;

ALTER TABLE devices
ADD CONSTRAINT fk_device_types
	FOREIGN KEY (type_id)
	REFERENCES device_types(id)
	ON DELETE RESTRICT,
ADD CONSTRAINT fk_vendors
	FOREIGN KEY (vendor_id)
	REFERENCES vendors(id)
	ON DELETE RESTRICT,
ADD CONSTRAINT uc_device
	UNIQUE (serial_number);
	
ALTER TABLE device_types
ADD CONSTRAINT uc_device_type
	UNIQUE (name);
	
ALTER TABLE vendors
ADD CONSTRAINT uc_vendor
	UNIQUE (name);
	
ALTER TABLE device_vlans
ADD CONSTRAINT fk_dv_devices 
	FOREIGN KEY (device_id) 
	REFERENCES devices(id)
	ON DELETE CASCADE,
ADD CONSTRAINT fk_dv_vlans 
	FOREIGN KEY (vlan_id) 
	REFERENCES vlans(vlan_id)
	ON DELETE CASCADE;
	
ALTER TABLE device_snapshots
ADD CONSTRAINT fk_ds_devices 
	FOREIGN KEY (device_id) 
	REFERENCES devices(id)
	ON DELETE CASCADE;
	
CREATE INDEX idx_devices_hostname ON devices(hostname);
CREATE INDEX idx_devices_ip ON devices(ip_address);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_priority ON devices(priority);
CREATE INDEX idx_interfaces_device_id ON interfaces(device_id);
CREATE INDEX idx_snapshots_device_id ON device_snapshots(device_id);
CREATE INDEX idx_snapshots_timestamp ON device_snapshots(timestamp);
CREATE INDEX idx_ih_interface_id ON interface_history(interface_id);
CREATE INDEX idx_ih_timestamp ON interface_history(timestamp);
CREATE INDEX idx_interfaces_device_status 
	ON interfaces(device_id, oper_status);