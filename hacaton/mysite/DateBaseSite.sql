CREATE TABLE "Events" (
	"Name" TEXT,
	"Place" TEXT,
	"Time" TIME,
	"Complete" BOOLEAN,
	"Discription" TEXT,
	PRIMARY KEY("Name")
);




CREATE TABLE "Persons" (
	"Id" INTEGER,
	"Name" TEXT,
	"Trouble" TEXT,
	"DateCmplete" DATE,
	PRIMARY KEY("Id")
);




CREATE TABLE "Questions" (
	"Id" INTEGER,
	"Question" TEXT,
	"Answer" TEXT,
	PRIMARY KEY("Id")
);


