import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MarketCloseComponent } from './market-close.component';

describe('MarketCloseComponent', () => {
  let component: MarketCloseComponent;
  let fixture: ComponentFixture<MarketCloseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MarketCloseComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MarketCloseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
