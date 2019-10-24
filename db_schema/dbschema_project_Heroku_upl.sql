CREATE SCHEMA "public";

CREATE  TABLE "public".demand_offer ( 
	id                   integer  NOT NULL ,
	demand_offer         varchar(100)  NOT NULL ,
	CONSTRAINT pk_offer_demand_id PRIMARY KEY ( id )
 );

CREATE  TABLE "public".requests_status ( 
	id                   integer  NOT NULL ,
	status               varchar(500)  NOT NULL ,
	CONSTRAINT pk_request_status_id PRIMARY KEY ( id )
 );

CREATE  TABLE "public".services ( 
	id                   integer  NOT NULL ,
	category             varchar(100)  NOT NULL ,
	CONSTRAINT pk_services_id PRIMARY KEY ( id )
 );

CREATE  TABLE "public".users ( 
	id                   integer  NOT NULL ,
	first_name           varchar(100)  NOT NULL ,
	surname              varchar(100)  NOT NULL ,
	email                varchar(100)  NOT NULL ,
	telephone            varchar(20)  NOT NULL ,
	address              varchar(100)   ,
	"password"           varchar(20)  NOT NULL ,
	CONSTRAINT pk_table_id PRIMARY KEY ( id )
 );

CREATE  TABLE "public".users_services ( 
	id                   integer  NOT NULL ,
	id_users             integer  NOT NULL ,
	id_services          integer  NOT NULL ,
	id_demand_offer      integer  NOT NULL ,
	CONSTRAINT pk_users_services_id PRIMARY KEY ( id )
 );

CREATE  TABLE "public".requests ( 
	id                   integer  NOT NULL ,
	id_user_demand       integer   ,
	id_users_offer       integer  NOT NULL ,
	id_services          integer   ,
	"timestamp"          timestamp  NOT NULL ,
	date_time            timestamp  NOT NULL ,
	add_information      varchar(500)   ,
	id_requests_status   integer   ,
	CONSTRAINT pk_requests_id PRIMARY KEY ( id )
 );

ALTER TABLE "public".requests ADD CONSTRAINT fk_users_demand FOREIGN KEY ( id_user_demand ) REFERENCES "public".users( id );

ALTER TABLE "public".requests ADD CONSTRAINT fk_users_offer FOREIGN KEY ( id_users_offer ) REFERENCES "public".users( id );

ALTER TABLE "public".requests ADD CONSTRAINT fk_requests_status FOREIGN KEY ( id_requests_status ) REFERENCES "public".requests_status( id );

ALTER TABLE "public".requests ADD CONSTRAINT fk_services FOREIGN KEY ( id_services ) REFERENCES "public".services( id );

ALTER TABLE "public".users_services ADD CONSTRAINT fk_users FOREIGN KEY ( id_users ) REFERENCES "public".users( id );

ALTER TABLE "public".users_services ADD CONSTRAINT fk_demand_offer FOREIGN KEY ( id_demand_offer ) REFERENCES "public".demand_offer( id );

ALTER TABLE "public".users_services ADD CONSTRAINT fk_services FOREIGN KEY ( id_services ) REFERENCES "public".services( id );
