# WebFaker

Make a fake site to cheat others for catching their passwords.

## Use default template

```shell
python fakesite.py tmpl TITLE
```

The tool will generate a website according to title. and log `/login` traffic.

## Clone a target http/https website.

```shell
python fakesite.py clone http(s)://yourtarget.com/ --path /login.jsp
```

The tool will enable proxy mode and logging `/login.jsp` traffic.

### Extension

By add --ext to specified a py extension, and `ext.py` file should be a template.


## Specified a local HTML project.

```shell
python fakesite.py spec <HTML PROJECT> --path /login
```

The tool will listen in <HTML PROJECT> and set `index.html` as default page. You must put all static files like `.js` file to `static` folder. And you can modify the function in `web.py` to response your own data. 

---

Note: All logged traffic data will be write to `record.csv` file in cwd.
