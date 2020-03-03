const posts = document.getElementById('posts');
const posts_json = JSON.parse(posts.innerHTML);

//posts
const updates = posts_json['data']['updates'];


const faculty_info = document.getElementById('faculty_info');
const faculty_json = JSON.parse(faculty_info.innerHTML);

const courses_info = document.getElementById('courses_info');
const courses_json = JSON.parse(courses_info.innerHTML);


//existing elements
var table = document.getElementById('posts_table');
var courses_list = document.getElementById('courses-list');
var faculty = document.getElementById('faculty');


//posts loop
for (var i = 0; i < updates.length; i++) {

    var row = document.createElement('tr');
    var td_date = document.createElement('td');
    var td_body = document.createElement('td');

    td_date.innerHTML = updates[i]['timestamp'].split(' ')[0];

    if (updates[i]['attachments'].file != null) {


        //files array (file)
        var file = updates[i]['attachments'].file;
        for (var x = 0; x < file.length; x++) {

            var file_link = document.createElement('a');
            file_link.href = file[x]['url'];
            file_link.innerHTML = file[x]['name'];

            td_body.innerHTML = updates[i]['body'] + '<br/>' + '<b>Downloads</b> ';
            td_body.appendChild(file_link);

        }
    } else {

        td_body.innerHTML = updates[i]['body'];
    }



    row.appendChild(td_date);
    row.appendChild(td_body);

    table.appendChild(row);

}

//courses loop
var li = document.createElement('li');
var a = document.createElement('a');

for (var j = 0; j < courses_json.length; j++) {

    a.href = courses_json[j]['href'];
    a.innerHTML = courses_json[j]['text'];

    courses_list.appendChild(li).appendChild(a);

}


//faculty info
faculty.innerHTML = '&nbsp;&nbsp;&nbsp;&nbsp;<b>Author: </b>' + faculty_json['first_name'] + ' ' + faculty_json['last_name'];
