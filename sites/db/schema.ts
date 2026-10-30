import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";
// Temporary game state and abuse controls only. No identity/research ingestion.
export const records=sqliteTable('records',{
  key:text('key').primaryKey(),kind:text('kind').notNull(),value:text('value').notNull(),
  expires:integer('expires').notNull(),version:integer('version').notNull().default(0)
});
export const leases=sqliteTable('leases',{
  key:text('key').primaryKey(),owner:text('owner').notNull(),expires:integer('expires').notNull()
});
export const counters=sqliteTable('counters',{
  key:text('key').primaryKey(),value:integer('value').notNull(),expires:integer('expires').notNull()
});
