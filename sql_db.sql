create table if not exists Mainmenu (
    id integer primary key autoincrement,
    title text not null,
    url text not null
);

create table if not exists Users (
    user_id integer primary key autoincrement,
    username varchar(255) not null,
    email varchar(255) not null, 
    psw varchar(255) not null,
    avatar blob default null,
    date_registered date
);

create table if not exists Posts (
    post_id integer primary key autoincrement,
    user_id integer not null,
    title varchar(255) not null, 
    post_content text not null,
    tags varchar(255) not null,
    post_img blob default null,
    date_posted date,
    foreign key (user_id) references Users(user_id)
);

create table if not exists Comments (
    comment_id integer primary key autoincrement,
    user_id integer,
    post_id integer,
    comment_content text,
    date_commented date,
    foreign key (user_id) references Users(user_id),
    foreign key (post_id) references Posts(post_id)
);

create table if not exists Tags (
    tag_id integer primary key autoincrement,
    tag_text text
);


