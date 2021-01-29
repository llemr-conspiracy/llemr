function dateString(date) {
    const dateOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    };
    return new Date(date).toLocaleDateString(undefined, dateOptions);
}

export default dateString;