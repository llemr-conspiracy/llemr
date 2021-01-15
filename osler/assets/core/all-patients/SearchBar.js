import React from 'react';
import { useAsyncDebounce} from 'react-table'


function SearchBar({
    globalFilter,
    setGlobalFilter,
  }) {
    const [value, setValue] = React.useState(globalFilter)
    const onChange = useAsyncDebounce(value => {
      setGlobalFilter(value || undefined)
    }, 200)
  
    return (
    <div className="form-group">
        <label htmlFor="all-patients-filter-input"  className="sr-only" >Filter</label>
        <div className="input-group">
            <div className="input-group-addon"><span className="glyphicon glyphicon-search" aria-hidden="true"></span></div>
            <input 
                value={value || ""}
                onChange={e => {
                    setValue(e.target.value);
                    onChange(e.target.value);
                }}
                type="text" 
                id="all-patients-filter-input" 
                placeholder="Filter by patient name" 
                className="form-control" 
            />
        </div>
    </div>
    );
}

export default SearchBar;