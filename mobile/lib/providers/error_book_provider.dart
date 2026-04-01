import 'package:flutter/material.dart';
import '../models/error_book.dart';
import '../services/api_service.dart';

class ErrorBookProvider extends ChangeNotifier {
  final ApiService _api = ApiService();

  List<ErrorBook> _errorBooks = [];
  ErrorBook? _selectedErrorBook;
  List<ErrorBookItem> _selectedItems = [];
  bool _isLoading = false;

  List<ErrorBook> get errorBooks => _errorBooks;
  ErrorBook? get selectedErrorBook => _selectedErrorBook;
  List<ErrorBookItem> get selectedItems => _selectedItems;
  bool get isLoading => _isLoading;

  List<ErrorBook> get pendingBooks =>
      _errorBooks.where((b) => b.isPending).toList();
  List<ErrorBook> get approvedBooks =>
      _errorBooks.where((b) => b.isApproved).toList();

  Future<void> loadErrorBooks({String? status}) async {
    _isLoading = true;
    notifyListeners();

    try {
      final data = await _api.listErrorBooks(status: status);
      _errorBooks = data.map((e) => ErrorBook.fromJson(e)).toList();
    } catch (_) {}

    _isLoading = false;
    notifyListeners();
  }

  Future<void> loadErrorBookDetail(int id) async {
    _isLoading = true;
    notifyListeners();

    try {
      final data = await _api.getErrorBook(id);
      _selectedErrorBook = ErrorBook.fromJson(data['error_book']);
      _selectedItems = (data['items'] as List)
          .map((e) => ErrorBookItem.fromJson(e))
          .toList();
    } catch (_) {}

    _isLoading = false;
    notifyListeners();
  }

  Future<ErrorBook?> generateErrorBook(String sessionId, {String subject = 'other'}) async {
    _isLoading = true;
    notifyListeners();

    try {
      final data = await _api.generateErrorBook(sessionId, subject: subject);
      final book = ErrorBook.fromJson(data);
      _errorBooks.insert(0, book);
      _isLoading = false;
      notifyListeners();
      return book;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  Future<bool> approveErrorBook(int id, bool approved, {String? reason}) async {
    try {
      await _api.approveErrorBook(id, approved, reason: reason);
      await loadErrorBooks();
      return true;
    } catch (_) {
      return false;
    }
  }
}
