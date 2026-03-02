export interface FileRoot {
	key: string;
	label: string;
	path: string;
}

export interface FileEntry {
	name: string;
	type: 'directory' | 'file';
	size: number;
	modified: string;
	extension: string;
	category: string;
}

export interface DirectoryListing {
	path: string;
	parent: string | null;
	entries: FileEntry[];
}
