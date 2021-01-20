import React from 'react';
import { useAsyncDebounce } from 'react-table'
import { BsSearch } from "react-icons/bs";
import InputGroup from "react-bootstrap/InputGroup";
import FormControl from "react-bootstrap/FormControl";


function SearchBar({
  globalFilter,
  setGlobalFilter,
}) {
  const [value, setValue] = React.useState(globalFilter)
  const onChange = useAsyncDebounce(value => {
    setGlobalFilter(value || undefined)
  }, 200)

  return (
    <InputGroup className="mb-3">
      <InputGroup.Prepend>
        <InputGroup.Text id="search-addon"><BsSearch /></InputGroup.Text>
      </InputGroup.Prepend>
      <FormControl
        aria-label="search bar"
        aria-describedby="search-addon"
        id="all-patients-filter-input"
        placeholder="Filter by patient name"
        value={value || ""}
        onChange={e => {
          setValue(e.target.value);
          onChange(e.target.value);
        }}
      />
    </InputGroup>
  );
}

export default SearchBar;