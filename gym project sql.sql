create database gym_management;

use gym_management;



CREATE TABLE membership_types (
    plan_id INT PRIMARY KEY auto_increment,
    plan_type VARCHAR(50),
    duration_days INT,
    cost_of_plan INT
);




CREATE TABLE trainer (
    trainer_id INT PRIMARY KEY AUTO_INCREMENT,
    trainer_name VARCHAR(50),
    phone_no VARCHAR(50) UNIQUE,
    joined_date DATE,
    specialization VARCHAR(100),
    salary DECIMAL(10,2)
);


CREATE TABLE members (
    member_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    phone VARCHAR(50),
    joined_date DATE,
    plan_id INT,
    expiry_date DATE,
    status VARCHAR(50),
    trainer_id INT,
    FOREIGN KEY (plan_id) REFERENCES membership_types(plan_id),
    FOREIGN KEY (trainer_id) REFERENCES trainer(trainer_id)
);


CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT,
    amount DECIMAL(10,2),
    payment_date DATE,
    plan_id INT,
    receipt_status VARCHAR(50),
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (plan_id) REFERENCES membership_types(plan_id)
);

CREATE TABLE member_attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT,
    check_in_date DATE,
    check_in_time TIME,
    check_out_time TIME,
    status VARCHAR(50),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE trainer_attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    trainer_id INT,
    check_in_date DATE,
    check_in_time TIME,
    check_out_time TIME,
    status VARCHAR(50),
    FOREIGN KEY (trainer_id) REFERENCES trainer(trainer_id)
);

CREATE TABLE trainer_payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    trainer_id INT,
    amount DECIMAL(10,2),
    payment_date DATE,
    payment_month VARCHAR(20),
    status VARCHAR(50),
    expiry_date Date,
    FOREIGN KEY (trainer_id) REFERENCES trainer(trainer_id)
);


select * from members;
select * from membership_types;
select * from payments;
select * from trainer;
select * from trainer_attendance;
select * from member_attendance; 
select * from trainer_payments;









