const format = number => number.toString().padStart(2, '0');

const clock = () => {
    const time = new Date();
    const year = time.getFullYear();
    const month = format(time.getMonth() + 1);
    const date = format(time.getDate());
    const hour = format(time.getHours());
    const minute = format(time.getMinutes());
    const second = format(time.getSeconds());
    const string = year + month + date + hour + minute + second + '&nbsp;';
    document.getElementById('now').innerHTML = string;
    setTimeout(clock, 1000);
};

clock();
