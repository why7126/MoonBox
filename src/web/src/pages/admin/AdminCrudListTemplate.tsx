import { ReactNode } from "react";

type FilterControl = {
  id: string;
  node: ReactNode;
};

type Column = {
  key: string;
  label: string;
  className?: string;
};

type AdminCrudListTemplateProps = {
  eyebrow: string;
  title: string;
  description: string;
  primaryAction?: ReactNode;
  filters: FilterControl[];
  columns: Column[];
  tableClassName?: string;
  colgroup?: ReactNode;
  isLoading?: boolean;
  loadingText?: string;
  emptyText?: string;
  rowCount: number;
  children: ReactNode;
  pagination: {
    label: string;
    totalLabel: string;
    total: number;
    totalUnit: string;
    page: number;
    pageCount: number;
    pageSize: number;
    pageSizeOptions: number[];
    onPageChange: (page: number) => void;
    onPageSizeChange: (pageSize: number) => void;
  };
  toast?: string;
};

export function AdminCrudListTemplate({
  eyebrow,
  title,
  description,
  primaryAction,
  filters,
  columns,
  tableClassName,
  colgroup,
  isLoading = false,
  loadingText = "正在加载...",
  emptyText = "暂无数据",
  rowCount,
  children,
  pagination,
  toast,
}: AdminCrudListTemplateProps) {
  const safePageCount = Math.max(1, pagination.pageCount);

  return (
    <>
      <section className="admin-content">
        <header className="admin-page-head">
          <div>
            <p>{eyebrow}</p>
            <h1>{title}</h1>
            <span>{description}</span>
          </div>
          {primaryAction && <div className="admin-head-actions">{primaryAction}</div>}
        </header>

        <div className="admin-toolbar">
          {filters.map((filter) => (
            <div className="admin-filter-control" key={filter.id}>
              {filter.node}
            </div>
          ))}
        </div>

        <div className="admin-table-wrap">
          <table className={`admin-table${tableClassName ? ` ${tableClassName}` : ""}`}>
            {colgroup}
            <thead>
              <tr>
                {columns.map((column) => (
                  <th className={column.className} key={column.key}>
                    {column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={columns.length} className="admin-table-state">
                    {loadingText}
                  </td>
                </tr>
              ) : rowCount === 0 ? (
                <tr>
                  <td colSpan={columns.length} className="admin-table-state">
                    {emptyText}
                  </td>
                </tr>
              ) : (
                children
              )}
            </tbody>
          </table>
        </div>

        <footer className="admin-pagination" aria-label={pagination.label}>
          <div className="admin-pagination-total">
            {pagination.totalLabel} <strong>{pagination.total}</strong> {pagination.totalUnit}
          </div>
          <div className="admin-pagination-actions">
            <button className="admin-page-btn page-icon" aria-label="上一页" disabled={pagination.page <= 1} onClick={() => pagination.onPageChange(pagination.page - 1)}>
              ‹
            </button>
            {Array.from({ length: safePageCount }, (_, index) => (
              <button key={index + 1} className={`admin-page-btn ${pagination.page === index + 1 ? "active" : ""}`} onClick={() => pagination.onPageChange(index + 1)}>
                {index + 1}
              </button>
            ))}
            <button className="admin-page-btn page-icon" aria-label="下一页" disabled={pagination.page >= safePageCount} onClick={() => pagination.onPageChange(pagination.page + 1)}>
              ›
            </button>
            <span className="admin-page-size-label">每页显示</span>
            <select className="admin-page-size" aria-label="每页显示条数" value={pagination.pageSize} onChange={(event) => pagination.onPageSizeChange(Number(event.target.value))}>
              {pagination.pageSizeOptions.map((option) => (
                <option key={option} value={option}>
                  {option} 条
                </option>
              ))}
            </select>
          </div>
        </footer>
      </section>
      {toast && <div className="admin-toast" role="status">{toast}</div>}
    </>
  );
}

export function AdminModalBackdrop({ children }: { children: ReactNode }) {
  return <div className="admin-modal-backdrop">{children}</div>;
}
