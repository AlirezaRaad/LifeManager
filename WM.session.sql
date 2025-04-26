DROP TABLE x;

SELECT  * FROM dailytasks;

CREATE TABLE x (id SERIAL PRIMARY KEY, taskName TEXT, parentTaskId INTEGER,
                        CONSTRAINT FK_self_parent_name FOREIGN KEY (parentTaskId) REFERENCES x(id)),
                        CONSTRAINT unique_rows UNIQUE(taskName, parentTaskId);

CREATE UNIQUE INDEX unique_null_parent_task ON x(taskName) WHERE parentTaskId IS NULL;

SELECT * FROM x;

INSERT INTO x (taskName,parentTaskId) VALUES ('ali',3);
INSERT INTO x (taskName) VALUES ('RE');
INSERT INTO x (taskName) VALUES ('ali');

