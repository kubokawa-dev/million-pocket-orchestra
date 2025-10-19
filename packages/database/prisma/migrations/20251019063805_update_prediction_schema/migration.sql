/*
  Warnings:

  - You are about to drop the `loto6_draws` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `numbers3_draws` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `numbers4_draws` table. If the table is not empty, all the data it contains will be lost.

*/
-- CreateEnum
CREATE TYPE "LotteryType" AS ENUM ('NUMBERS3', 'NUMBERS4', 'LOTO6', 'BINGO5', 'LOTO7', 'MINILOTO');

-- DropTable
DROP TABLE "public"."loto6_draws";

-- DropTable
DROP TABLE "public"."numbers3_draws";

-- DropTable
DROP TABLE "public"."numbers4_draws";

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "username" TEXT,
    "displayName" TEXT,
    "avatarUrl" TEXT,
    "bio" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "prediction_posts" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "drawId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "prediction_posts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "predictions" (
    "id" TEXT NOT NULL,
    "predictionPostId" TEXT NOT NULL,
    "numbers" JSONB NOT NULL,

    CONSTRAINT "predictions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "likes" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "predictionPostId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "likes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "comments" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "predictionPostId" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "isHidden" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "comments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "draws" (
    "id" TEXT NOT NULL,
    "lotteryType" "LotteryType" NOT NULL,
    "drawNumber" INTEGER NOT NULL,
    "drawDate" TIMESTAMP(3) NOT NULL,
    "winningNumbers" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "draws_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "users_username_key" ON "users"("username");

-- CreateIndex
CREATE INDEX "prediction_posts_userId_idx" ON "prediction_posts"("userId");

-- CreateIndex
CREATE INDEX "prediction_posts_drawId_idx" ON "prediction_posts"("drawId");

-- CreateIndex
CREATE INDEX "predictions_predictionPostId_idx" ON "predictions"("predictionPostId");

-- CreateIndex
CREATE INDEX "likes_predictionPostId_idx" ON "likes"("predictionPostId");

-- CreateIndex
CREATE INDEX "likes_userId_idx" ON "likes"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "likes_userId_predictionPostId_key" ON "likes"("userId", "predictionPostId");

-- CreateIndex
CREATE INDEX "comments_predictionPostId_idx" ON "comments"("predictionPostId");

-- CreateIndex
CREATE INDEX "comments_userId_idx" ON "comments"("userId");

-- CreateIndex
CREATE INDEX "comments_createdAt_idx" ON "comments"("createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "draws_lotteryType_drawNumber_key" ON "draws"("lotteryType", "drawNumber");

-- AddForeignKey
ALTER TABLE "prediction_posts" ADD CONSTRAINT "prediction_posts_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "prediction_posts" ADD CONSTRAINT "prediction_posts_drawId_fkey" FOREIGN KEY ("drawId") REFERENCES "draws"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "predictions" ADD CONSTRAINT "predictions_predictionPostId_fkey" FOREIGN KEY ("predictionPostId") REFERENCES "prediction_posts"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "likes" ADD CONSTRAINT "likes_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "likes" ADD CONSTRAINT "likes_predictionPostId_fkey" FOREIGN KEY ("predictionPostId") REFERENCES "prediction_posts"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "comments" ADD CONSTRAINT "comments_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "comments" ADD CONSTRAINT "comments_predictionPostId_fkey" FOREIGN KEY ("predictionPostId") REFERENCES "prediction_posts"("id") ON DELETE CASCADE ON UPDATE CASCADE;
