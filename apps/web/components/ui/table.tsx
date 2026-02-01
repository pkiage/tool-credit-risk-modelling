import type { ReactNode } from "react";

interface Column<T> {
	key: string;
	header: string;
	render?: (row: T) => ReactNode;
}

interface TableProps<T> {
	columns: Column<T>[];
	data: T[];
	className?: string;
}

export function Table<T extends Record<string, unknown>>({
	columns,
	data,
	className = "",
}: TableProps<T>) {
	return (
		<div className={`overflow-x-auto ${className}`}>
			<table className="min-w-full divide-y divide-gray-200">
				<thead className="bg-gray-50">
					<tr>
						{columns.map((col) => (
							<th
								key={col.key}
								className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
							>
								{col.header}
							</th>
						))}
					</tr>
				</thead>
				<tbody className="divide-y divide-gray-200 bg-white">
					{data.map((row, i) => (
						// biome-ignore lint/suspicious/noArrayIndexKey: generic table has no stable row ID
						<tr key={i} className="hover:bg-gray-50">
							{columns.map((col) => (
								<td key={col.key} className="whitespace-nowrap px-4 py-3 text-sm text-gray-900">
									{col.render ? col.render(row) : String(row[col.key] ?? "")}
								</td>
							))}
						</tr>
					))}
					{data.length === 0 && (
						<tr>
							<td colSpan={columns.length} className="px-4 py-8 text-center text-sm text-gray-500">
								No data available
							</td>
						</tr>
					)}
				</tbody>
			</table>
		</div>
	);
}
