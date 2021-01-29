function dateTimeString(date) {
    const dateOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
    };
    return new Date(date).toLocaleString(undefined, dateOptions);
}

export default dateTimeString;