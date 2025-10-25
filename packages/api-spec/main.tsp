import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using TypeSpec.Http;
using TypeSpec.Rest;

@service({
  title: "Million Pocket API",
})
@server("http://localhost:3000/api", "Development server")
@server("https://million-pocket.vercel.app/api", "Production server")
namespace MillionPocketAPI;

model Loto6Draw {
  draw_number: int32;
  draw_date: string;
  numbers: string;
  bonus_number: int32;
}

// ============================================
// Common Types
// ============================================

enum LotteryType {
  NUMBERS3,
  NUMBERS4,
  LOTO6,
}

enum HitStatus {
  exact,
  partial,
  miss,
}

// ============================================
// Models
// ============================================

model User {
  id: string;
  email: string;
  username?: string;
  displayName?: string;
  avatarUrl?: string;
  bio?: string;
  createdAt: utcDateTime;
  updatedAt: utcDateTime;
}

model Prediction {
  id: string;
  userId: string;
  lotteryType: LotteryType;
  numbers: string; // JSON array
  bonusNumber?: int32;
  confidence?: float32;
  reasoning?: string;
  targetDrawNumber?: int32;
  targetDrawDate?: utcDateTime;
  isPublic: boolean;
  isHidden: boolean;
  flagCount: int32;
  actualDrawNumber?: int32;
  actualNumbers?: string;
  actualBonusNumber?: int32;
  hitStatus?: HitStatus;
  hitCount?: int32;
  createdAt: utcDateTime;
  updatedAt: utcDateTime;
  
  // Aggregates
  likeCount?: int32;
  commentCount?: int32;
  isLikedByCurrentUser?: boolean;
}

model Like {
  id: string;
  userId: string;
  predictionId: string;
  createdAt: utcDateTime;
}

model Comment {
  id: string;
  userId: string;
  predictionId: string;
  content: string;
  isHidden: boolean;
  createdAt: utcDateTime;
  updatedAt: utcDateTime;
  
  // Populated
  user?: User;
}

// ============================================
// Request/Response Models
// ============================================

model PredictionCreateRequest {
  lotteryType: LotteryType;
  numbers: string; // JSON array
  bonusNumber?: int32;
  confidence?: float32;
  reasoning?: string;
  targetDrawNumber?: int32;
  targetDrawDate?: utcDateTime;
  isPublic: boolean;
}

model PredictionUpdateRequest {
  numbers?: string;
  bonusNumber?: int32;
  confidence?: float32;
  reasoning?: string;
  isPublic?: boolean;
}

model CommentCreateRequest {
  content: string;
}

model PredictionListResponse {
  predictions: Prediction[];
  total: int32;
  page: int32;
  pageSize: int32;
}

model ErrorResponse {
  message: string;
  code?: string;
}

// ============================================
// User Endpoints
// ============================================

@route("/users")
namespace Users {
  @get
  @route("/me")
  op getCurrentUser(): User | ErrorResponse;
  
  @patch
  @route("/me")
  op updateCurrentUser(@body user: {
    username?: string;
    displayName?: string;
    avatarUrl?: string;
    bio?: string;
  }): User | ErrorResponse;
}

// ============================================
// Prediction Endpoints (User-facing)
// ============================================

@route("/predictions")
namespace Predictions {
  @get
  op listPredictions(
    @query lotteryType?: LotteryType,
    @query userId?: string,
    @query page?: int32,
    @query pageSize?: int32,
  ): PredictionListResponse | ErrorResponse;
  
  @get
  @route("/{id}")
  op getPrediction(@path id: string): Prediction | ErrorResponse;
  
  @post
  op createPrediction(@body prediction: PredictionCreateRequest): Prediction | ErrorResponse;
  
  @patch
  @route("/{id}")
  op updatePrediction(
    @path id: string,
    @body prediction: PredictionUpdateRequest
  ): Prediction | ErrorResponse;
  
  @delete
  @route("/{id}")
  op deletePrediction(@path id: string): { message: string } | ErrorResponse;
  
  // Like endpoints
  @post
  @route("/{id}/like")
  op likePrediction(@path id: string): { message: string } | ErrorResponse;
  
  @delete
  @route("/{id}/like")
  op unlikePrediction(@path id: string): { message: string } | ErrorResponse;
  
  // Comment endpoints
  @get
  @route("/{id}/comments")
  op getComments(
    @path id: string,
    @query page?: int32,
    @query pageSize?: int32,
  ): {
    comments: Comment[];
    total: int32;
  } | ErrorResponse;
  
  @post
  @route("/{id}/comments")
  op createComment(
    @path id: string,
    @body comment: CommentCreateRequest
  ): Comment | ErrorResponse;
}

// ============================================
// Admin Endpoints
// ============================================

@route("/admin")
namespace Admin {
  @route("/predictions")
  namespace AdminPredictions {
    @get
    op listAllPredictions(
      @query page?: int32,
      @query pageSize?: int32,
      @query includeHidden?: boolean,
    ): PredictionListResponse | ErrorResponse;
    
    @patch
    @route("/{id}/hide")
    op hidePrediction(@path id: string): Prediction | ErrorResponse;
    
    @patch
    @route("/{id}/unhide")
    op unhidePrediction(@path id: string): Prediction | ErrorResponse;
    
    @patch
    @route("/{id}/result")
    op updatePredictionResult(
      @path id: string,
      @body result: {
        actualDrawNumber: int32;
        actualNumbers: string;
        actualBonusNumber?: int32;
        hitStatus: HitStatus;
        hitCount: int32;
      }
    ): Prediction | ErrorResponse;
  }
  
  @route("/comments")
  namespace AdminComments {
    @get
    op listAllComments(
      @query page?: int32,
      @query pageSize?: int32,
    ): {
      comments: Comment[];
      total: int32;
    } | ErrorResponse;
    
    @patch
    @route("/{id}/hide")
    op hideComment(@path id: string): Comment | ErrorResponse;
    
    @patch
    @route("/{id}/unhide")
    op unhideComment(@path id: string): Comment | ErrorResponse;
  }
  
  @route("/draws")
  namespace AdminDraws {
    // Numbers3
    @post
    @route("/numbers3")
    op createNumbers3Draw(@body draw: {
      draw_number: int32;
      draw_date: string;
      numbers: string;
    }): { message: string } | ErrorResponse;
    
    // Numbers4
    @post
    @route("/numbers4")
    op createNumbers4Draw(@body draw: {
      draw_number: int32;
      draw_date: string;
      numbers: string;
    }): { message: string } | ErrorResponse;
    
    // Loto6
    @post
    @route("/loto6")
    op createLoto6Draw(@body draw: {
      draw_number: int32;
      draw_date: string;
      numbers: string;
      bonus_number: int32;
    }): { message: string } | ErrorResponse;
  }
}

// ============================================
// Public Draw Results
// ============================================

@route("/loto6-draws")
@tag("Draws")
interface Loto6Draws {
  @get
  list(): Loto6Draw[];
}

@route("/sample")
@tag("Sample")
interface Sample {
  @get
  getSample(): Loto6Draw[];
}

@route("/draws")
namespace Draws {
  @get
  @route("/numbers3")
  op getNumbers3Draws(
    @query limit?: int32,
  ): {
    draws: {
      draw_number: int32;
      draw_date: string;
      numbers: string;
    }[];
  } | ErrorResponse;
  
  @get
  @route("/numbers4")
  op getNumbers4Draws(
    @query limit?: int32,
  ): {
    draws: {
      draw_number: int32;
      draw_date: string;
      numbers: string;
    }[];
  } | ErrorResponse;
  
  @get
  @route("/loto6")
  op getLoto6Draws(
    @query limit?: int32,
  ): {
    draws: {
      draw_number: int32;
      draw_date: string;
      numbers: string;
      bonus_number: int32;
    }[];
  } | ErrorResponse;
}
