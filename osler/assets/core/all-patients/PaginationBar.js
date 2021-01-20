import React from 'react';
import Pagination from 'react-bootstrap/Pagination'


function PaginationBar({
  canPreviousPage,
  canNextPage,
  pageOptions,
  pageCount,
  gotoPage,
  previousPage,
  nextPage,
  pageIndex,
}) {

  const minPage = 0;
  const maxPage = pageOptions.length - 1;
  const windowRadius = 2;
  const windowSize = 2 * windowRadius + 1;

  let left = Math.max(minPage, pageIndex - windowRadius);
  let right = Math.max(left + windowSize, pageIndex + windowRadius + 1);
  right = Math.min(maxPage + 1, right);

  if (left <= minPage + 2) {
    left = minPage;
  }

  if (right >= maxPage - 1) {
    right = maxPage + 1;
  }

  let items = [];

  if (left > minPage) {
    items.push(
      <Pagination.Item key={minPage} onClick={() => gotoPage(minPage)}>{minPage + 1}</Pagination.Item>,
      <Pagination.Ellipsis key={'min-ellipsis'} />
    );
  }

  for (let i = left; i < right; i++) {
    items.push(
      <Pagination.Item key={i} active={i === pageIndex} onClick={() => gotoPage(i)}>{i + 1}</Pagination.Item>
    );
  }

  if (right < maxPage + 1) {
    items.push(
      <Pagination.Ellipsis key={'max-ellipsis'} />,
      <Pagination.Item key={maxPage} onClick={() => gotoPage(maxPage)}>{maxPage + 1}</Pagination.Item>
    );
  }

  return (
    <Pagination>
      <Pagination.First onClick={() => gotoPage(0)} disabled={!canPreviousPage} />
      <Pagination.Prev onClick={() => previousPage()} disabled={!canPreviousPage} />
      {items}
      <Pagination.Next onClick={() => nextPage()} disabled={!canNextPage} />
      <Pagination.Last onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage} />
    </Pagination>
  );
}

export default PaginationBar;